import os
import sys
import yaml
from datetime import datetime, timezone

from dataclasses import dataclass, field
from ..helperFunctions.baseClass import baseClass
# from ..helperFunctions.dictFuncs import dcToDict,loadDict,saveDict

default_comment = f'''
Database project configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class spatiotemporalDefaults:
    latitude: float = None
    longitude: float = None
    altitude: float = None

@dataclass(kw_only=True)
class projectConfiguration(baseClass):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    projectPath: str = None
    dateCreated: str = None
    dateModified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    siteIDs: list = field(default_factory=lambda:['__TEMPLATE__'])
    defaultInterval: int = 1800 # Default averaging interval of the database in seconds
    safeMode: bool 

    def __post_init__(self):
        # baseClass will load configuration from this path if it exists
        self.configFile = os.path.join(self.projectPath,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveToYaml()


@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str
    config: projectConfiguration = None
    safeMode: bool = True

    def __post_init__(self):
        self.config = projectConfiguration(projectPath=self.projectPath,safeMode=self.safeMode)
        self.syncAttributes(self.config,overwrite=True)
        super().__post_init__()
        