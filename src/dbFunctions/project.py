import os
import sys
import yaml
from datetime import datetime, timezone

from dataclasses import dataclass, field
from ..helperFunctions.baseFunctions import baseFunctions
# from ..helperFunctions.dictFuncs import dcToDict,loadDict,saveDict

default_comment = f'''
Database project configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

# 
@dataclass(kw_only=True)
class projectConfiguration(baseFunctions):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    projectPath: str = None
    dateCreated: str = None
    dateModified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))
    siteIDs: list = field(default_factory=lambda:['__TEMPLATE__'])

    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveToYaml()


@dataclass(kw_only=True)
class project(baseFunctions):
    projectPath: str
    config: projectConfiguration = None

    def __post_init__(self):
        self.config = projectConfiguration(projectPath=self.projectPath)
        super().__post_init__()
        