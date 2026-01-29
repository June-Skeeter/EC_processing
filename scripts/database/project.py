import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from submodules.helperFunctions.baseClass import baseClass
from zoneinfo import ZoneInfo


default_comment = f'''
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str = field(repr=False)
    subPath: str = field(default='',repr=False,init=False)
    configName: str = field(default=None,init=False,repr=False)
    # depth: int = field(default=0,init=False,repr=False)

    def __post_init__(self):
        if self.projectPath is None:
            return
        self.projectPath = os.path.normpath(self.projectPath)
        if not type(self).__name__.endswith('Configuration'):
            self.syncConfig(projectConfiguration.from_dict(self.__dict__))
        if self.configName is not None:
            self.configFilePath = os.path.normpath(os.path.join(self.projectPath,self.subPath,self.configName))
        super().__post_init__()

    def syncConfig(self,config,dbg=False):
        config = config.from_dict(self.to_dict(keepNull=False)|{'projectPath':self.projectPath,'verbose':self.verbose})
        # self.depth+=1
        exclude = list(baseClass.__dataclass_fields__.keys()) + [k for k,v in project.__dataclass_fields__.items() if not v.repr]
        
        for key,value in config.__dict__.items():
            if (key not in exclude #and value is not None 
                and (key not in self.__dict__.keys() or self.__dict__[key] is None)
                ):
                setattr(self,key,value)

        
@dataclass(kw_only=True)
class projectConfiguration(project):
    fromFile: bool = field(default=True,repr=False)
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated 
    createdBy: str = field(default='')
    lastModified: str = field(default=None)
    projectDescription: str = field(default='')


    def __post_init__(self):
        self.configName = 'projectConfiguration.yml'
        super().__post_init__()
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.projectPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.rootPath}')

        # Only save if it is first time creating
        # Otherwise saves are performed where appropriate in child classes
        if not self.configFileExists or not self.readOnly:
            self.logWarning('Saving')
            self.saveConfigFile()
