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
            # if self.createdBy is None:
            #     self.logWarning('Missing "createdBy" parameter, please specify to proceed',verbose=True)
            #     self.createdBy = input('createdBy: ')
            self.saveConfigFile()



@dataclass(kw_only=True)
class siteConfiguration(spatialObject):
    configFileName: str = field(default='siteConfiguration.yml',repr=False)
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
        self.configFileRoot = os.path.join(self.projectPath,self.siteID)
        super().__post_init__()
        if not self.configFileExists:
            self.saveConfigFile(keepNull=False)


@dataclass(kw_only=True)
class dataSourceConfiguration(baseClass):
    configFileName: str = field(default='dataSourceConfiguration.yml',repr=False)
    projectPath: str = field(repr=False)
    siteID: str
    dataSourceID: str
    systemConfiguration: dict = field(default_factory=dict)
    sourceFileConfiguration: Iterable = None
    
    def __post_init__(self):
        self.siteConfiguration = siteConfiguration(projectPath=self.projectPath,siteID=self.siteID,verbose=False)
        self.configFileRoot = os.path.join(self.projectPath,self.siteID,self.dataSourceID)
        super().__post_init__()
        self.systemCheck()

        if self.sourceFileConfiguration is not None:
            if is_dataclass(self.sourceFileConfiguration):
                self.sourceFileConfiguration = self.sourceFileConfiguration.to_dict()
            else:
                self.sourceFileConfiguration = rawFile.sourceFile(
                    fileFormat=self.sourceFileConfiguration['fileFormat'],
                    fileName=self.sourceFileConfiguration['fileName'],
                    traceMetadataMap = self.systemConfiguration.traceMetadataMap,
                    verbose=self.verbose,
                    configFileRoot=self.configFileRoot,
                    ).parseMetadata()#.to_dict(keepNull=False)
        # self.sourceFileConfiguration.saveConfigFile(keepNull=False)
        # self.systemConfiguration.saveConfigFile(keepNull=False)
        if not self.configFileExists or not self.safeMode:
            sourceFileConfiguration_DC = self.sourceFileConfiguration
            self.sourceFileConfiguration = self.sourceFileConfiguration.to_dict(keepNull=False)
            systemConfiguration_DC = self.systemConfiguration
            self.systemConfiguration = self.systemConfiguration.to_dict(keepNull=False)
            self.saveConfigFile(keepNull=False) 
            self.sourceFileConfiguration = sourceFileConfiguration_DC
            self.systemConfiguration = systemConfiguration_DC


    def systemCheck(self):
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

