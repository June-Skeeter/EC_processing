import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass


default_comment = f'''
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class project(baseClass):

    startDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Start Date will parse from string input (assuming Year-Month-Day order) For nested values, defaults to parent object, provide to override',
    })
    endDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Start Date will parse from string input (assuming Year-Month-Day order) For nested values, defaults to parent object, provide to override',
    })
    timezone: str = field(
        default = 'UTC',
        metadata = {
            'description': 'UTC offset.  For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })

    projectPath: str = field(repr=False)
    subPath: str = field(default=None,repr=False,init=False)
    depth: int = field(default=0,init=False,repr=False)

    def __post_init__(self):
        
        if self.projectPath is None:
            return
        if not type(self).__name__.endswith('Configuration'):
            self.syncConfig(projectConfiguration.from_dict(self.__dict__))
        self.rootPath = self.projectPath
        if self.subPath:
            self.rootPath = os.path.join(self.rootPath,self.subPath)
        super().__post_init__()

    def syncConfig(self,config,dbg=False):
        config = config.from_dict(self.to_dict(keepNull=False)|{'projectPath':self.projectPath})
        self.depth+=1
        exclude = list(baseClass.__dataclass_fields__.keys()) + [k for k,v in project.__dataclass_fields__.items() if not v.repr]
        
        for key,value in config.__dict__.items():
            if (key not in exclude #and value is not None 
                and (key not in self.__dict__.keys() or self.__dict__[key] is None)
                ):
                setattr(self,key,value)
            # else:
            #     if key not in exclude:
        

@dataclass(kw_only=True)
class projectConfiguration(project):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated 

    createdBy: str = field(default='')
    lastModified: str = field(default=None)
    projectDescription: str = field(default='')

    def __post_init__(self):
        super().__post_init__()
        
        if os.path.isdir(self.rootPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.rootPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.rootPath}')

        # Only save if it is first time creating
        # Otherwise saves are performed where appropriate in child classes
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile()
