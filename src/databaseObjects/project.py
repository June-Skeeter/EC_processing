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
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    projectPath: str
    dateModified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    # defaultInterval: int = 1800 # Default averaging interval of the database in seconds
    # safeMode: bool 

    def __post_init__(self):
        # baseClass will load configuration from this path if it exists
        self.configFile = os.path.join(self.projectPath,type(self).__name__+'.yml')
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFile):
            self.logChoice(f'Create New Project in {self.projectPath}')
        super().__post_init__()
        self.saveConfigFile()


@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str
    projectConfig: projectConfiguration = field(
        init=False,
        repr=False
    )
    safeMode: bool = field(
        default=False,
        repr=False
    )

    def __post_init__(self):
        if self.projectPath:
            self.projectConfig = projectConfiguration(
                projectPath=self.projectPath,
                verbose=self.verbose
                )
        super().__post_init__()
        