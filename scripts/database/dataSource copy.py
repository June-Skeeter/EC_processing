import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from dataclasses import is_dataclass
from scripts.database.site import site
from scripts.database.project import configCommon
import scripts.database.dataLoggers as dataLoggers
from scripts.database.dbTools import database
import submodules.helperFunctions.dictFuncs as dictFuncs
from scripts.database.sensorModels import sensorModels
import scripts.rawDataProcessing.parseCSI as parseCSI
import scripts.rawDataProcessing.parseCSV as parseCSV
from ruamel.yaml.comments import CommentedMap
import fnmatch
import numpy as np

mdMap = site.metadataMap

@dataclass(kw_only=True)
class dataSource(site):
    dataSourceID: str
    fileInventory: dict = field(default_factory=dict,init=False,repr=False)
    rawFileParsers: dict = field(init=False,repr=False,default_factory=lambda:{
        'TOB3':parseCSI.TOB3,
        'TOA5':parseCSI.TOA5,
        'mixedArray':parseCSI.mixedArray,
        'HOBOcsv':parseCSV.HOBOcsv,
    })
    # sourceDir: str = None
    
    def __post_init__(self):
        if self.UID is None:
            self.formatUID('dataSourceID')
        if not type(self).__name__.endswith('dataSourceConfiguration'):
            self.debug = True
            self.syncConfig(dataSourceConfiguration)
        super().__post_init__()
 

    def dbDump(self,sourceDir,stageID = None):
        dbInstance = database(projectPath=self.projectPath)
    
        if stageID is None:
            self.stageID = os.path.join(self.measurementType,self.dataSourceID)
        else:
            self.stageID = stageID

        if not os.path.isdir(sourceDir):
            self.logError(msg=f'Invalid search directory {sourceDir}')
        
        subPath = os.path.sep.join(['siteMetadata',self.siteID,'dataSources'])
        inventoryName = os.path.join(self.projectPath,subPath,f"{self.dataSourceID}_fileInventory.json")

        if os.path.isfile(inventoryName):
            self.fileInventory = self.loadDict(fileName=inventoryName)
            fileInventory = dictFuncs.unpackDict(self.fileInventory)
        else:
            fileInventory = {}
        updateSourceConfig = False
        for dir,_,fname in os.walk(sourceDir):
            fname = [os.path.join(dir,f) for f in fname if fnmatch.fnmatch(f,self.filenameMatch)]
            fname = [f for f in fname if (f not in fileInventory or type(fileInventory[f]) is not bool)]
            if len(fname)>0:
                result = []
                for f in fname:
                    print(f)
                    data = self.readSourceFile(filename=f)
                    out = dbInstance.writeDataFrame(data=data,siteID=self.siteID,stageID=self.stageID)
                    result.append(out)
                    if out: 
                        for col in data.columns:
                        # update dateRange as relevant
                            ix = data[~data[col].isna()].index
                            dr = self.traceMetadata[col]['dateRange']
                            if len(dr) == 0:
                                self.traceMetadata[col]['dateRange'] = [ix.min().to_pydatetime(),ix.max().to_pydatetime()]
                                updateSourceConfig = True
                            else:
                                if self.traceMetadata[col]['dateRange'][0]>ix.min():
                                    self.traceMetadata[col]['dateRange'][0]=ix.min().to_pydatetime()
                                    updateSourceConfig = True
                                    
                                if self.traceMetadata[col]['dateRange'][1]<ix.max():
                                    self.traceMetadata[col]['dateRange'][1]=ix.max().to_pydatetime()
                                    updateSourceConfig = True

                self.fileInventory = dictFuncs.updateDict(self.fileInventory,dictFuncs.packDict(fname,base=sourceDir,fill=result))

        
        if updateSourceConfig:
            dataSourceConfiguration.from_class(self,{'readOnly':False,'projectPath':self.projectPath})

        self.saveDict(self.fileInventory,fileName=inventoryName)

    def readSourceFile(self,filename,extractData=True):
        if self.fileFormat not in self.rawFileParsers:
            self.logError(f'Files from {self.dataLogger["manufacturer"]} logger of type {self.fileFormat} not yet supported')
            
        elif self.fileFormat not in ['mixedArray'] and self.filenameMatch and not fnmatch.fnmatch(os.path.split(filename)[-1],self.filenameMatch):
            self.logError(f'Template file: {os.path.split(filename)[-1]} does not match expected pattern {self.filenameMatch}')
            
        sourceFile = self.rawFileParsers[self.fileFormat](
            fileName=filename,
            extractData=extractData,
            traceMetadata=self.traceMetadata.copy(),
            verbose=self.verbose,
            debug=self.debug
            )
        if not extractData:
            return(sourceFile)
        data = sourceFile.dataTable
        data.index = sourceFile.datetimeTrace.datetime
        if self.timezone == 'UTC':
            data.index = data.index.tz_localize(self.timezone)
        else:
            self.logError('Implement UTC conversion for dbDumping')
        keep = [
            value['fileName'] for value in self.traceMetadata.values()
            if not value['ignore'] and value['fileName'] in data.columns]
        data = data[keep]
        if self.startDate is not None:
            data = data.loc[data.index>=self.startDate]
        if self.endDate is not None:
            data = data.loc[data.index<=self.endDate]
        duplicates = data.index.duplicated()
        if duplicates.sum()>0:
            self.logMessage(f'Removed n={duplicates.sum()} rows at positions: {data.index[duplicates]}')
            data = data[~duplicates].copy()
        return(data)

      
headerText = f'''
Datasource configuration file defines key parameters for individual data sources.
An data source, is any set of files sharing common metadata, e.g. GHG files from an EC station with common configuration settings.
When settings change significantly (e.g., instrumentation swap) the configuration is not common and the files should be treated as having separate sources.
Values defined here (e.g., startDate) are shared with nested sub-site objects (e.g., dataSource) unless explicitly defined in the dataSourceConfiguration
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''      

@dataclass(kw_only=True)
class dataSourceConfiguration(configCommon,dataSource):
    header: str = field(default=headerText,repr=False,init=False) # YAML header, must be treated differently

    dataSourceID: str = field(
        metadata=mdMap('Unique dataSourceID code')
    )
    siteID: str = field(
        metadata=mdMap('Unique siteID code, must correspond to an existing site. Site-level metadata (e.g. startDate, coordinates, etc.) will be propagated to any undefined values in the dataSourceConfiguration wherever applicable.')
    )
    measurementType: str = field(
        metadata=mdMap('Code describing the type of measurement the source corresponds to', options=['EC','BIOMET','Met','Manual','Model'])
        )
    description: str = field(
        default = None,
        metadata=mdMap('self explanatory')
    )
    fileFormat: str = field(
        default=None,
        metadata=mdMap('Format of sourceFile. Must correspond to a class Method defined in the rawProcessingModule e.g., TOB3 is defined in parseCIS.py',options=['TOB3','TOA5','GHG','HOBOcsv','mixedArray'])
        )
    templateFile: Iterable = field(
        default=None,
        metadata=mdMap('Representative template file for parsing variable names etc.')
    )
    filenameMatch: str = field(
        default=None,
        metadata=mdMap('Regex wildcard pattern for file matching.')
    )
    dataLogger: Iterable = field(
        default_factory=lambda:dataLoggers.dataLogger().to_dict(),
        metadata=mdMap('Data logger metadata'))
    sensorInventory: Iterable = field(
        default_factory=dict,
        metadata=mdMap('List or dict of sensor objects, will dump to dict, but supports list of inputs'))
    traceMetadata: dict = field(
        default_factory=dict,
        metadata=mdMap('dict describing traces in the source File')
        )

    def __post_init__(self):
        self.configName = f"{self.dataSourceID}_sourceConfig.yml"
        self.subPath = os.path.sep.join(['siteMetadata',self.siteID,'dataSources'])
        self.logWarning('Fix formatSpaceTimeFields order?')
        self.formatSpaceTimeFields()
        super().__post_init__()
        self.formatDataLogger()
        self.formatSensors()
        if type(self.templateFile) is str:
            self.traceMetadata = self.parseMetadata(self.templateFile)
        elif type(self.templateFile) is list:
            tempMetadata = {}
            for templateFile in self.templateFile:
                tempMetadata = self.parseMetadata(templateFile,tempMetadata)
            self.traceMetadata = tempMetadata
        elif self.templateFile is not None:
            self.logError('Invalid templateFile formatting')
        # if not self.configFileExists or not self.readOnly:
        if not self.readOnly:
            self.saveConfigFile(keepNull=False)

    def formatDataLogger(self):
        if type(self.dataLogger) is str:
            if hasattr(dataLoggers,self.dataLogger):
                self.dataLogger = getattr(dataLoggers,self.dataLogger)().to_dict()
            else:
                self.logError(f'Could not find data logger: {self.dataLogger}')
        elif is_dataclass(self.dataLogger):
            self.dataLogger = self.dataLogger.to_dict()
        elif type(self.dataLogger) in [dict,CommentedMap] and 'loggerModel' in self.dataLogger:
            self.dataLogger=getattr(dataLoggers,self.dataLogger['loggerModel']).from_dict(self.dataLogger).to_dict()
        elif type(self.dataLogger) in [dict,CommentedMap]:
            self.dataLogger=dataLoggers.dataLogger.from_dict(self.dataLogger).to_dict()
        else:
            breakpoint()
            self.logError(msg=f"Cannot handle dataLogger object: {self.dataLogger}")
        
    def parseMetadata(self,templateFile,tempMetadata={}):
        sourceAttributes = self.readSourceFile(filename=templateFile,extractData=False)
        for key,value in self.dataLogger.items():
            if (value == self.__dataclass_fields__['dataLogger'].default_factory()[key]) and hasattr(sourceAttributes,key):
                self.dataLogger[key] = getattr(sourceAttributes,key)
            elif hasattr(sourceAttributes,key) and getattr(sourceAttributes,key) != self.dataLogger[key]:
                if type(self.dataLogger[key]) != list:
                    self.dataLogger[key] = [self.dataLogger[key]]
                self.dataLogger[key].append(getattr(sourceAttributes,key))
        tempMetadata = dictFuncs.updateDict(tempMetadata,sourceAttributes.traceMetadata)
        for key in tempMetadata:
            if tempMetadata[key]['sensorID'] == '':
                self.logMessage(f'{key} missing sensor association, ignore defaulting to True')
                tempMetadata[key]['ignore'] = True
            if self.startDate is not None and self.endDate is not None:
                tempMetadata[key]['dateRange']=[self.startDate,self.endDate]
        return(tempMetadata)

    def formatSensors(self):
        #If list of sensor objects dump to dict
        temp = {}
        if type(self.sensorInventory) is list:
            for sI in self.sensorInventory:
                while sI.UID in temp:
                    sI.updateUID()
                temp[sI.UID] = sI.to_dict(keepNull=False)
            self.sensorInventory = temp
        else:
            for sI in self.sensorInventory.values():
                sI = sensorModels[sI['sensorModel']].from_dict(sI)
                if sI.sensorID in temp:
                    sI.updateUID()
                temp[sI.sensorID] = sI.to_dict(keepNull=False)
            self.sensorInventory = temp
        EC = {'sonic':[],'irga':[],'thermocouple':[]}
        for sI in self.sensorInventory.values():
            if 'variables' in sI and sI['variables'] != []:
                for v in sI['variables']:
                    if v in self.traceMetadata:
                        self.traceMetadata[v]['sensorID'] = sI['sensorID']
                    else:
                        self.traceMetadata[v] = {'sensorID':sI['sensorID']}
            if sI['sensorFamily'] == 'EC':
                if 'sonic' in sI['sensorType']:
                    EC['sonic'].append(sI)
                if 'irga' in sI['sensorType']:
                    EC['irga'].append(sI)
                if 'thermocouple' in sI['sensorType']:
                    self.logError('thermocouple not added yet')
        if EC['sonic'] != []:
            self.formatEC(EC)

    def formatEC(self,EC):
        nsonic = len(EC['sonic'])
        measurementHeight = EC['sonic'][0]['measurementHeight']
        northOffset = EC['sonic'][0]['northOffset']
        if nsonic>1:
            self.logError('Secondary sonics yet to be implemented')
        for irga in EC['irga']:
            if not 'northwardSeparation' in irga:
                n,e=self.geographicSeparation(northOffset,irga['xSeparation'],irga['ySeparation'])
                irga['northwardSeparation'],irga['eastwardSeparation']=n,e
            elif irga['northwardSeparation']+irga['eastwardSeparation'] == 0:
                pass
            elif not 'xSeparation' in irga:
                x,y=self.cartesianSeparation(northOffset)
                irga['xSeparation'],irga['ySeparation']=x,y
            else:
                self.logWarning('Add coordinate check?',verbose=True,traceback=True)
        
    def geographicSeparation(self,northOffset,xSeparation,ySeparation):
        # Convert to radians
        # **Note**: north offset is relative to geographic (meteorologic) north, while x,y offsets are in cartesian coordinates.  To perform the coordinate rotation properly theta must be converted to cartesian coordinate (positive is counter-clockwise from the x axis)
        theta = np.deg2rad(270-northOffset)
        # Calculate counter-clockwise rotation matrix
        R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        # Evaluate rotation matrix.
        v = np.array([[xSeparation,ySeparation]])
        Rv = (R*v)
        Rv = Rv.sum(axis=1).round(3)
        northwardSeparation = float(Rv[1])
        eastwardSeparation = float(Rv[0])
        return(northwardSeparation,eastwardSeparation)
    
    def cartesianSeparation(self,northOffset,northwardSeparation,eastwardSeparation):
        # Get the inverse of geographic separation
        # If xy not provided, calculate, if provided along with north/south check values make sense
        theta = np.deg2rad(northOffset-270)
        R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
        v = np.array([[eastwardSeparation,northwardSeparation]])
        Rv = (R*v)
        Rv = Rv.sum(axis=1).round(3)
        xSeparation = float(Rv[0])
        ySeparation = float(Rv[1])
        return (xSeparation,ySeparation)



# @dataclass(kw_only=True)
# class measurementSystem(baseClass):
#     measurementType: str = field(default=None,repr=False,
#                             metadata={'options':['EC','BIOMET','Manual']})
    
#     measurementHeight: float = field(default = None, metadata=mdMap('Measurement height (Zm) in meters, of reference sonic'},repr=False)
#     northOffset: float = field(default = None, metadata=mdMap('Offset from North in degrees (clockwise) of reference sonic'},repr=False)
#     # canopyHeight: float = None
#     dataLogger: Iterable = field(default_factory=dict)
#     sensorConfigurations: Iterable = field(default_factory=dict)

#     def __post_init__(self):

#         if type(self.dataLogger) is str:
#             if hasattr(dataLoggers,self.dataLogger):
#                 self.dataLogger = getattr(dataLoggers,self.dataLogger)().to_dict()
#             else:
#                 self.logError(f'Could not find data logger: {self.dataLogger}')
#         elif is_dataclass(self.dataLogger):
#             self.dataLogger = self.dataLogger.to_dict()
#             print(self.dataLogger)
#         elif type(self.dataLogger) is dict and 'loggerModel' in self.dataLogger:
#             self.dataLogger=getattr(dataLoggers,self.dataLogger).from_dict(self.dataLogger).to_dict()
#         elif type(self.dataLogger) is dict:
#             self.dataLogger=dataLoggers.dataLogger.from_dict(self.dataLogger).to_dict()
#         else:
#             self.logError(msg=f"Cannot handle dataLogger object: {self.dataLogger}")

#         sensorDict = {}
        
#         if type(self.sensorConfigurations) is dict:
#             self.sensorConfigurations = list(self.sensorConfigurations.values())
#         for sensor in self.sensorConfigurations:
#             if is_dataclass(sensor):
#                 sensor = sensor.to_dict()
#             if 'sensorModel' not in sensor:
#                 self.logError('must provide sensorModel')
#             elif sensor['sensorModel'] not in sensorModels:
#                 self.logError(f'Sensor not currently supported: {sensor["sensorModel"]}')
#             model = sensorModels[sensor['sensorModel']].from_dict(sensor)
#             while model.UID in sensorDict.keys():
#                 model.updateUID()
#                 model.sensorID = model.UID
#             sensorDict[model.UID] = model.to_dict(keepNull=False)

#         self.sensorConfigurations = sensorDict
#         super().__post_init__()

#         if self.measurementType == 'EC':
#             self.formatEC()

#     def formatEC(self):
#         nsonic = 0
#         for key,value in self.sensorConfigurations.items():
#             if value['sensorType'].startswith('sonic'):
#                 nsonic += 1
#                 if self.measurementHeight is None or self.northOffset is None:
#                     self.measurementHeight = value['measurementHeight']
#                     self.northOffset = value['northOffset']
#                 if nsonic>1 and all([v==0.0 or v is None for k,v in value.items() if k.endswith('Separation')]):
#                     if value['measurementHeight'] != self.measurementHeight:
#                         self.sensorConfigurations[key]['verticalSeparation'] = round(value['measurementHeight']-self.measurementHeight,3)
#                         self.logWarning('Separation parameters for secondary sonic not specified, but different measurment heights are.  Inferring verticalSeparation from measurment heights, assuming horizontal allignement')
#                     else:
#                         self.logError('At least one non-zero separation parameter (North/South/Vertical or X,Y,Z) required for valid secondary sonic position')
#             if 'northwardSeparation' not in value or 'eastwardSeparation' not in value or 'verticalSeparation' not in value:
#                 if 'xSeparation' in value and 'ySeparation' in value and 'verticalSeparation' in value:
#                     value['northwardSeparation'],value['eastwardSeparation']=self.geographicSeparation(value['xSeparation'],value['ySeparation'])
#                 elif 'irga' in value['sensorType']:
#                     self.logError('Separation parameters (North/South/Vertical or X,Y,Z) are required for all IRGAs')

#     def geographicSeparation(self,xSeparation,ySeparation):
#         # Convert to radians
#         # **Note**: north offset is relative to geographic (meteorologic) north, while x,y offsets are in cartesian coordinates.  To perform the coordinate rotation properly theta must be converted to cartesian coordinate (positive is counter-clockwise from the x axis)
#         theta = np.deg2rad(270-self.northOffset)
#         # Calculate counter-clockwise rotation matrix
#         R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
#         # Evaluate rotation matrix.
#         v = np.array([[xSeparation,ySeparation]])
#         Rv = (R*v)
#         Rv = Rv.sum(axis=1).round(3)
#         northwardSeparation = float(Rv[1])
#         eastwardSeparation = float(Rv[0])
#         return(northwardSeparation,eastwardSeparation)
    
#     def cartesianSeparation(self,northwardSeparation,eastwardSeparation):
#         # Get the inverse of geographic separation
#         # If xy not provided, calculate, if provided along with north/south check values make sense
#         theta = np.deg2rad(self.northOffset-270)
#         R = np.array([[np.cos(theta),-np.sin(theta)],[np.sin(theta),np.cos(theta)]])
#         v = np.array([[eastwardSeparation,northwardSeparation]])
#         Rv = (R*v)
#         Rv = Rv.sum(axis=1).round(3)
#         xSeparation = float(Rv[0])
#         ySeparation = float(Rv[1])
#         return (xSeparation,ySeparation)
    
# @dataclass(kw_only=True)
# class CustomFlux(measurementSystem):
#     measurementType: str = field(default='EC',repr=False)
#     SONIC: str = field(repr=False)
#     CO2: str = field(default=None,repr=False)
#     CH4: str = field(default=None,repr=False)

#     def __post_init__(self):
#         super().__post_init__()
#         self.sensorConfigurations = [
#             sensorModels[self.SONIC](
#                     measurementHeight=self.measurementHeight,
#                     northOffset=self.northOffset)
#         ]
#         if self.CO2 is not None:
#             self.sensorConfigurations += [
#             sensorModels[self.CO2]()
#         ]
    

# @dataclass(kw_only=True)
# class EasyFlux_IRGASON_LI7700(measurementSystem):
    
#     measurementType: str = field(default='EC',repr=False)
#     xSeparation: float = field(default=None,repr=False)
#     ySeparation: float = field(default=None,repr=False)
#     zSeparation: float = field(default=None,repr=False)
    
#     def __post_init__(self):
#         if self.dataLogger == {}:
#             self.dataLogger = dataLoggers.CR1000X().to_dict(keepNull=False)
#         if self.sensorConfigurations == {}:
#             self.sensorConfigurations = [
#                 sensorModels['IRGASON'](
#                     measurementHeight=self.measurementHeight,
#                     northOffset=self.northOffset
#                     ),
#                 sensorModels['LI7700'](
#                     xSeparation=self.xSeparation,
#                     ySeparation=self.ySeparation,
#                     zSeparation=self.zSeparation),
#                 sensorModels['CSI_T107']()
#             ]
#         super().__post_init__()


# class SmartFlux_7500_7700(measurementSystem):
#     pass

# class SmartFlux_7200_7700(measurementSystem):
#     pass