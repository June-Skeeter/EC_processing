import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from dataclasses import is_dataclass
from modules.database.site import site
import modules.database.dataLoggers as dataLoggers
from modules.helperFunctions.baseClass import baseClass
from modules.database.sensorModels import sensorModels
import modules.rawDataProcessing.rawFile as rawFile
import numpy as np


default_comment = f'''
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class dataSource(site):
    dataSourceID: str
    
    def __post_init__(self):
        if self.UID is None:
            self.formatUID('dataSourceID')
        if not type(self).__name__.endswith('dataSourceConfiguration'):
            self.syncConfig(dataSourceConfiguration)
        super().__post_init__()
            
@dataclass(kw_only=True)
class dataSourceConfiguration(dataSource):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated differently

    dataSourceID: str = field(
        metadata = {'description': 'Unique dataSourceID code'} 
    )
    measurementType: str = field(
        default='measurement',
                            metadata={'options':['EC','BIOMET','Met','Manual','Model']}
                            )
    sourceSystemMetadata: dict = field(
        default_factory=dict,
        metadata={
            'description':'Contains information on the measurement system collecting the data'
        })
    modelDescription: dict = field(
        default_factory=dict,
        metadata={
            'description':'Contains information on the model producing the data'
        })
    sourceFileMetadata: Iterable = field(
        default=None,
        metadata={
            'description':'a system object, which contains information on the system collecting the data'
    })
    
    lastModified: str = field(default=None)

    def __post_init__(self):
        self.subPath = os.path.sep.join(['configurationFiles',self.siteID,'dataSources'])#self.dataSourceID])
        self.configName = f"{self.dataSourceID}_sourceConfig.yml"
        self.logWarning('Fix formatSpaceTimeFields order?')
        self.formatSpaceTimeFields()
        super().__post_init__()
        if self.measurementType != 'Model':
            self.modelDescription = None
            if self.sourceSystemMetadata == {}:
                breakpoint()
            self.sourceSystemMetadata = sourceSystemMetadata.from_dict(self.sourceSystemMetadata|{'verbose':self.verbose,'measurementType':self.measurementType}).to_dict(keepNull=False)
        else:
            self.sourceSystemMetadata = None
        # if self.sourceFileMetadata is not None and 'traceMetadata' in self.sourceFileMetadata:
        #     traceMetadata = self.sourceFileMetadata['traceMetadata']
        # else:
        #     traceMetadata = {}
        #     print('z?')
        # print(traceMetadata)
        if self.sourceFileMetadata is None:
            self.sourceFileMetadata = baseClass(verbose=self.verbose).to_dict()
        elif type(self.sourceFileMetadata) is str:
            if self.sourceSystemMetadata['dataLogger']['manufacturer'] == 'CSI':
                self.sourceFileMetadata = rawFile.sourceFile(
                    fileName=self.sourceFileMetadata,
                    sourceFileType=self.sourceSystemMetadata['dataLogger']['manufacturer'],
                    # traceMetadata=traceMetadata,
                    verbose=self.verbose
                    ).parseMetadata()
            else:
                self.logError('Logger files not yet supported')
        else:
            self.sourceFileMetadata = rawFile.sourceFile.from_dict(
                    self.sourceFileMetadata|{
                        'sourceFileType':self.sourceSystemMetadata['dataLogger']['manufacturer'],
                        # 'traceMetadata':traceMetadata,
                        'verbose':self.verbose
                        }).parseMetadata()
        if self.startDate is not None and self.endDate is not None:
            for key in self.sourceFileMetadata['traceMetadata'].keys():
                self.sourceFileMetadata['traceMetadata'][key]['dateRange'] = [self.startDate,self.endDate]
                
        if self.sourceFileMetadata == {}:
            breakpoint()
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile(keepNull=False)

@dataclass(kw_only=True)
class sourceSystemMetadata(baseClass):
    measurementType: str = field(default=None,repr=False,
                            metadata={'options':['EC','BIOMET','Manual']})
    
    measurementHeight: float = field(default = None, metadata = {'description': 'Measurement height (Zm) in meters, of reference sonic'},repr=False)
    northOffset: float = field(default = None, metadata = {'description': 'Offset from North in degrees (clockwise) of reference sonic'},repr=False)
    # canopyHeight: float = None
    dataLogger: Iterable = field(default_factory=dict)
    sensorConfigurations: Iterable = field(default_factory=dict)

    def __post_init__(self):

        if type(self.dataLogger) is str:
            if hasattr(dataLoggers,self.dataLogger):
                self.dataLogger = getattr(dataLoggers,self.dataLogger)().to_dict()
            else:
                self.logError(f'Could not find data logger: {self.dataLogger}')
        elif is_dataclass(self.dataLogger):
            self.dataLogger = self.dataLogger.to_dict()
            
        sensorDict = {}
        
        if type(self.sensorConfigurations) is dict:
            self.sensorConfigurations = list(self.sensorConfigurations.values())
        for sensor in self.sensorConfigurations:
            if is_dataclass(sensor):
                sensor = sensor.to_dict()
            if 'sensorModel' not in sensor:
                self.logError('must provide sensorModel')
            elif sensor['sensorModel'] not in sensorModels:
                breakpoint()
                self.logError(f'Sensor not currently supported: {sensor["sensorModel"]}')
            model = sensorModels[sensor['sensorModel']].from_dict(sensor)
            while model.UID in sensorDict.keys():
                model.updateUID()
                model.sensorID = model.UID
            sensorDict[model.UID] = model.to_dict(keepNull=False)

        self.sensorConfigurations = sensorDict
        super().__post_init__()

        if self.measurementType == 'EC':
            self.formatEC()

    def formatEC(self):
        nsonic = 0
        for key,value in self.sensorConfigurations.items():
            if value['sensorType'].startswith('sonic'):
                nsonic += 1
                if self.measurementHeight is None or self.northOffset is None:
                    self.measurementHeight = value['measurementHeight']
                    self.northOffset = value['northOffset']
                if nsonic>1 and all([v==0.0 or v is None for k,v in value.items() if k.endswith('Separation')]):
                    if value['measurementHeight'] != self.measurementHeight:
                        self.sensorConfigurations[key]['verticalSeparation'] = round(value['measurementHeight']-self.measurementHeight,3)
                        self.logWarning('Separation parameters for secondary sonic not specified, but different measurment heights are.  Inferring verticalSeparation from measurment heights, assuming horizontal allignement')
                    else:
                        self.logError('At least one non-zero separation parameter (North/South/Vertical or X,Y,Z) required for valid secondary sonic position')
            if 'northwardSeparation' not in value or 'eastwardSeparation' not in value or 'verticalSeparation' not in value:
                if 'xSeparation' in value and 'ySeparation' in value and 'verticalSeparation' in value:
                    value['northwardSeparation'],value['eastwardSeparation']=self.geographicSeparation(value['xSeparation'],value['ySeparation'])
                elif 'irga' in value['sensorType']:
                    self.logError('Separation parameters (North/South/Vertical or X,Y,Z) are required for all IRGAs')

    def geographicSeparation(self,xSeparation,ySeparation):
        # Convert to radians
        # **Note**: north offset is relative to geographic (meteorologic) north, while x,y offsets are in cartesian coordinates.  To perform the coordinate rotation properly theta must be converted to cartesian coordinate (positive is counter-clockwise from the x axis)
        theta = np.deg2rad(270-self.northOffset)
        # Calculate counter-clockwise rotation matrix
        R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        # Evaluate rotation matrix.
        v = np.array([[xSeparation,ySeparation]])
        Rv = (R*v)
        Rv = Rv.sum(axis=1).round(3)
        northwardSeparation = float(Rv[1])
        eastwardSeparation = float(Rv[0])
        return(northwardSeparation,eastwardSeparation)
    
    def cartesianSeparation(self,northwardSeparation,eastwardSeparation):
        # Get the inverse of geographic separation
        # If xy not provided, calculate, if provided along with north/south check values make sense
        theta = np.deg2rad(self.northOffset-270)
        R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        v = np.array([[eastwardSeparation,northwardSeparation]])
        Rv = (R*v)
        Rv = Rv.sum(axis=1).round(3)
        xSeparation = float(Rv[0])
        ySeparation = float(Rv[1])
        return (xSeparation,ySeparation)
    
@dataclass(kw_only=True)
class CustomFlux(sourceSystemMetadata):
    measurementType: str = field(default='EC',repr=False)
    SONIC: str = field(repr=False)
    CO2: str = field(default=None,repr=False)
    CH4: str = field(default=None,repr=False)

    def __post_init__(self):
        super().__post_init__()
        self.sensorConfigurations = [
            sensorModels[self.SONIC](
                    measurementHeight=self.measurementHeight,
                    northOffset=self.northOffset)
        ]
        if self.CO2 is not None:
            self.sensorConfigurations += [
            sensorModels[self.CO2]()
        ]
    

@dataclass(kw_only=True)
class EasyFlux_IRGASON_LI7700(sourceSystemMetadata):
    
    measurementType: str = field(default='EC',repr=False)
    xSeparation: float = field(default=None,repr=False)
    ySeparation: float = field(default=None,repr=False)
    zSeparation: float = field(default=None,repr=False)
    
    def __post_init__(self):
        if self.dataLogger == {}:
            self.dataLogger = dataLoggers.CR1000X().to_dict(keepNull=False)
        if self.sensorConfigurations == {}:
            self.sensorConfigurations = [
                sensorModels['IRGASON'](
                    measurementHeight=self.measurementHeight,
                    northOffset=self.northOffset
                    ),
                sensorModels['LI7700'](
                    xSeparation=self.xSeparation,
                    ySeparation=self.ySeparation,
                    zSeparation=self.zSeparation),
                sensorModels['CSI_T107']()
            ]
        else:
            breakpoint()
        super().__post_init__()


class SmartFlux_7500_7700(sourceSystemMetadata):
    pass

class SmartFlux_7200_7700(sourceSystemMetadata):
    pass