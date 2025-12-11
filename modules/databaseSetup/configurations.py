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
    sourceSystemConfiguration: dict = field(default_factory=dict)
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
                    variableSensorMap = self.sourceSystemConfiguration.variableSensorMap,
                    verbose=self.verbose,
                    configFileRoot=self.configFileRoot,
                    ).parseMetadata()#.to_dict(keepNull=False)
        self.sourceFileConfiguration = self.sourceFileConfiguration.to_dict(keepNull=False)
        self.sourceSystemConfiguration = self.sourceSystemConfiguration.to_dict(keepNull=False)
        # self.sourceFileConfiguration.saveConfigFile(keepNull=False)
        # self.sourceSystemConfiguration.saveConfigFile(keepNull=False)
        if not self.configFileExists or not self.safeMode:

            self.saveConfigFile(keepNull=False) 

    def systemCheck(self):
        if is_dataclass(self.sourceSystemConfiguration):
            self.sourceSystemConfiguration = self.sourceSystemConfiguration.to_dict()
        if hasattr(systemTypes,self.sourceSystemConfiguration['systemType']):
            system = getattr(systemTypes,self.sourceSystemConfiguration['systemType'])
            self.sourceSystemConfiguration = system.from_dict(self.sourceSystemConfiguration|{
                'configFileRoot':self.configFileRoot,
                'configFileName':'sourceSystemConfiguration.yml'})
        else:
            self.logError('System type not yet supported')

