from dataclasses import dataclass, field
from typing import Iterable
import numpy as np
from dataclasses import is_dataclass
from modules.databaseSetup.spatialObject import spatialObject
import modules.databaseSetup.sensorModels as sensorModels
import modules.databaseSetup.dataLoggers as dataLoggers


# dataclasses to define default values for different data systems
# can be used to add simple checks on parameters
# avoid adding significant functionally here

@dataclass(kw_only=True)
class system(spatialObject):
    # configFileName: str = 'systemConfiguration.yml'
    verbose: bool = field(default=False,repr=False)
    systemType: str = field(init=False)
    # dataFormat: str = None
    # dataInterval: float = field(default=None,metadata={'description':'Interval of dataset in seconds'})
    dataLogger: Iterable = field(default_factory=dict)
    sensorConfigurations: Iterable = field(default_factory=dict)
    traceMetadataMap: Iterable = field(default=None)
    
    def __post_init__(self):
        if not hasattr(self,'systemType'):
            self.systemType = type(self).__name__
        UD = {}
        if type(self.dataLogger) is str:
            if hasattr(dataLoggers,self.dataLogger):
                self.dataLogger = getattr(dataLoggers,self.dataLogger)()
            else:
                self.logError('Could not find datalogger')
        if type(self.sensorConfigurations) is dict:
            self.sensorConfigurations = list(self.sensorConfigurations.values())
        for sensor in self.sensorConfigurations:
            if is_dataclass(sensor):
                sensor = sensor.to_dict()
            if not hasattr(sensorModels,sensor['sensorModel']):
                self.logError('Sensor not currently supported')
            model = getattr(sensorModels,sensor['sensorModel']).from_dict(sensor)
            while model.UID in UD.keys():
                model.updateUID()
            # if hasattr(sensor,'traceMetadataMap') and len(sensor.traceMetadataMap)>0:
            #     for var in sensor.traceMetadataMap:
            #         self.traceMetadataMap[var] = {}
            #         self.traceMetadataMap[var]['sensorID'] = model.UID
            #         for key,val in model.traceMetadataMap[var].items():
            #             self.traceMetadataMap[var][key] = val
            # elif hasattr(model,'defaultTraceMap'):
            #     for var in model.defaultTraceMap:
            #         self.traceMetadataMap[var] = {}
            #         for key,val in model.defaultTraceMap[var].items():
            #             self.traceMetadataMap[var][key] = val
            #         self.traceMetadataMap[var]['sensorID'] = model.UID

            UD[model.UID] = model.to_dict(keepNull=False)

        self.sensorConfigurations = UD
        super().__post_init__()

@dataclass(kw_only=True)
class Manual(system):
    pass

@dataclass(kw_only=True)
class External(system):
    systemType: str = 'External'
    dataLogger: str = field(init=False,default=None)
    sensorConfigurations: str = field(init=False,default=None)

@dataclass(kw_only=True)
class BIOMET(system):
    pass
    # systemType:str = 'BIOMET'

@dataclass(kw_only=True)
class EC(system):
    measurementHeight: float = field(default = None, metadata = {'description': 'Measurement height (Zm) in meters, of reference sonic'})
    northOffset: float = field(default = None, metadata = {'description': 'Offset from North in degrees (clockwise) of reference sonic'})
    canopyHeight: float = None

    # systemType:str = 'EC'
    def __post_init__(self):
        # if self.dataInterval is not None and self.dataInterval > 1:
        #     self.logError(f"dataInterval is invalid for EC system: {self.dataInterval} s ")
        super().__post_init__()
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
    
class SmartFlux(EC):
    systemType: str = 'EC'


@dataclass(kw_only=True)
class IRGASON_LI7700(EC):
    systemType: str = 'EC'
    xSeparation: float = field(default=None,repr=False)
    ySeparation: float = field(default=None,repr=False)
    zSeparation: float = field(default=None,repr=False)
    traceMetadataMap: str ='EasyFlux'
    
    def __post_init__(self):
        if self.dataLogger == {}:
            self.dataLogger = dataLoggers.CR1000X().to_dict(keepNull=False)
        if self.sensorConfigurations == {}:
            self.sensorConfigurations = [
                sensorModels.IRGASON(
                    measurementHeight=self.measurementHeight,
                    northOffset=self.northOffset
                    ),
                sensorModels.LI7700(
                    xSeparation=self.xSeparation,
                    ySeparation=self.ySeparation,
                    zSeparation=self.zSeparation),
                sensorModels.CSI_T107()
            ]
        else:
            breakpoint()
        super().__post_init__()