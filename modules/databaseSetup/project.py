import os
import sys
import yaml
from datetime import datetime, timezone

from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass

default_comment = f'''
Database project configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class projectConfiguration(baseClass):
    verbose:str = None
    projectPath: str
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    dateModified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))

    def __post_init__(self):
        self.configFilePath = os.path.join(self.projectPath,type(self).__name__+'.yml')
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.projectPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.projectPath}')
        super().__post_init__()
        self.dateModified = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        self.saveConfigFile()


@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str = field(repr=False)
    projectConfiguration: dict = field(default_factory=dict)

    def __post_init__(self):
        self.projectConfiguration = projectConfiguration(projectPath=self.projectPath)
        super().__post_init__()