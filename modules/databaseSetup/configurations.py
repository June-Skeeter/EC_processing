import os
from typing import Iterable
from dataclasses import is_dataclass
from datetime import datetime, timezone
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.databaseSetup.spatialObject import spatialObject
import modules.databaseSetup.systemTypes as systemTypes
import modules.databaseSetup.sensorModels as sensorModels
import modules.rawDataProcessing.rawFile as rawFile

default_comment = f'''
File Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''
@dataclass(kw_only=True)
class projectConfiguration(baseClass):
    configFileName: str = field(default='projectConfiguration.yml',repr=False)
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated differently

    projectPath: str
    dateModified: str = field(default=None)
    createdBy: str = field(default=None)
    structure: dict = field(default_factory=lambda:{
        'configFiles':None,
        'database':None,
        'highFrequencyData':None
        })

    def __post_init__(self):
        self.configFileRoot = self.projectPath
        # baseClass will load configuration (if it exists) and perform type-enforcement
        super().__post_init__()
        
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.projectPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.projectPath}')
        self.dateModified = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

        # Only save if it is first time creating
        # Otherwise saves are performed where appropriate in child classes
        if not self.configFileExists:
            self.saveConfigFile()
            for sub in self.structure:
                os.makedirs(os.path.join(self.projectPath,sub))



@dataclass(kw_only=True)
class siteConfiguration(spatialObject):
    configFileName: str = field('siteConfiguration.yml',repr=False)
    projectPath: str = field(repr=False)
    siteID: str
    siteName: str = field(
        default = None,
        metadata = {'description': 'Name of the Site'} 
    )
    PI: str = field(
        default = None,
        metadata = {'description': 'Principal Investigator(s)'} 
    )

    def __post_init__(self):
        self.projectConfiguration = projectConfiguration(projectPath=self.projectPath,verbose=False)
        self.logMessage(self.projectConfiguration.logFile,verbose=False)
        self.configFileRoot = os.path.join(self.projectPath,'configFiles',self.siteID)
        super().__post_init__()
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile(keepNull=False)
            self.projectConfiguration.close()




@dataclass(kw_only=True)
class dataSourceConfiguration(baseClass):
    configFileName: str = field(default='dataSourceConfiguration.yml',repr=False)
    projectPath: str = field(repr=False)
    siteID: str
    dataSourceID: str
    systemConfiguration: dict = field(default_factory=dict)
    sourceFile: Iterable = None
    
    def __post_init__(self):
        self.siteConfiguration = siteConfiguration(projectPath=self.projectPath,siteID=self.siteID,verbose=False)
        self.configFileRoot = os.path.join(self.projectPath,self.siteID,self.dataSourceID)
        super().__post_init__()
        self.systemConfig()
        self.fileConfig()
        if not self.configFileExists or not self.readOnly:
            self.systemConfiguration_DC = self.systemConfiguration
            self.systemConfiguration = self.systemConfiguration.to_dict(keepNull=False)
            self.sourceFile_DC = self.sourceFile
            self.sourceFile = self.sourceFile.to_dict(keepNull=False)
            self.saveConfigFile(keepNull=False) 
            self.sourceFile = self.sourceFile_DC
            self.systemConfiguration = self.systemConfiguration_DC

    def systemConfig(self):
        if is_dataclass(self.systemConfiguration):
            self.systemConfiguration = self.systemConfiguration.to_dict()
        if hasattr(systemTypes,self.systemConfiguration['systemType']):
            system = getattr(systemTypes,self.systemConfiguration['systemType'])
            self.systemConfiguration = system.from_dict(self.systemConfiguration|{
                'configFileRoot':self.configFileRoot,
                'configFileName':'systemConfiguration.yml'})
        else:
            self.logError('System type not yet supported')
        for key,value in self.systemConfiguration.__dict__.items():
            if value is None and hasattr(self.siteConfiguration,key):
                siteProp = getattr(self.siteConfiguration,key)
                # If value is not present, default to site parameter, allows for paramters (e.g. lat/lon) to differe if needed
                setattr(self.systemConfiguration,key,siteProp)

    def fileConfig(self):
        if self.sourceFile is None:
            self.sourceFile = baseClass()
        elif is_dataclass(self.sourceFile):
            self.logError('DC input not supported')
        elif type(self.sourceFile) is str:
            if self.systemConfiguration.dataLogger['manufacturer'] == 'CSI':
                self.sourceFile = rawFile.sourceFile(
                    fileName=self.sourceFile,
                    sourceType=self.systemConfiguration.dataLogger['manufacturer'],
                    traceMetadataMap=self.systemConfiguration.traceMetadataMap,
                    verbose=self.verbose
                    ).parseMetadata()
            else:
                self.logError('Logger files not yet supported')
        else:
            self.sourceFile = rawFile.sourceFile.from_dict(
                self.sourceFile|{
                    'sourceType':self.systemConfiguration.dataLogger['manufacturer'],
                    'verbose':self.verbose
                    }).parseMetadata()
