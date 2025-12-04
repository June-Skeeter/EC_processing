import os
# from typing import Iterable
from dataclasses import dataclass, field, MISSING

# from modules.helperFunctions.getClasses import getClasses
from src.databaseObjects.project import project
from src.siteSetup.siteObjects import siteObject
import src.siteSetup.loggerObjects as loggerObjects




@dataclass(kw_only=True)
class dataSource(project):
    siteID: str
    systemID: str
    stationName: str = None
    loggerModel: str = None
    serialNumber: str = None
    program: str = None
    siteConfig: dict = field(init=False,repr=False)
    sourceFileName: str = field(
        default = None,
        repr = False,
        metadata={
            'descriptions': 'Name of the raw data file'
            })
    templateFileName: str = field(
        default = None,
        metadata={
            'descriptions': 'Name of the template data file, if provided instead of sourceFileName, will only extract metadata'
            })
    extractData: bool = field(
        default=True,
        repr=False,
        metadata={
            'description':'True (all data) / False (preview header where applicable)'
            })
    
    def __post_init__(self):
        if self.projectPath:
            self.configFile = os.path.join(self.projectPath,self.siteID,'dataSources',type(self).__name__,self.systemID+'.yml')
        super().__post_init__()
        self.siteConfig = siteObject(
            projectPath = self.projectPath,
            projectConfig = self.projectConfig,
            siteID = self.siteID,
            safeMode = True
            )
        # breakpoint()
        if not hasattr(self,'sourceFileName') and self.templateFileName is not None:
            self.sourceFileName = self.templateFileName

        self.processFile()
        if 'dataLogger' in self.siteConfig.dataSystems[self.systemID]:
            loggerDict = self.siteConfig.dataSystems[self.systemID]['dataLogger']
            if hasattr(loggerObjects,self.loggerModel):
                loggerClass = getattr(loggerObjects,self.loggerModel)
            else:
                loggerClass = loggerObjects.dataLogger
            for key,value in loggerDict.items():
                if key in self.__dict__.keys() and value != self.__dict__[key]:
                    if value == loggerClass.__dataclass_fields__[key].default:
                        loggerDict[key] = self.__dict__[key]
                        self.logMessage(f'Updating {key} in {self.siteConfig.relativeConfigPath}')
                        self.siteConfig.saveConfigFile(verbose=False)
                    else:
                        self.logWarning('Issue in logger variable')
                        self.logChoice('Proceed with interactive debug session')
                        breakpoint()
        if not self.safeMode or not self.configStatus:
            self.saveConfigFile()
