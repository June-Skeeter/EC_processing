import os
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.databaseSetup.project import project

@dataclass(kw_only=True)
class siteConfiguration(baseClass):
    sitePath: str = field(init=False,repr=False)
    projectPath: str = field(repr=False)
    siteID: str
    
    def __post_init__(self):
        self.sitePath = os.path.join(self.projectPath,self.siteID)
        self.configFilePath = os.path.join(self.sitePath,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveConfigFile()

@dataclass(kw_only=True)
class site(project):
    siteID: str
    projectPath: str
    siteConfiguration: dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.siteConfiguration = siteConfiguration(
            siteID=self.siteID,
            projectPath=self.projectPath
            )