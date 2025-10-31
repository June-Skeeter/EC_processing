import os
import sys
from .project import project
# from ..helperFunctions.parseCoordinates import parseCoordinates
from dataclasses import dataclass, field
# from ruamel.yaml import YAML
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions

# yaml = YAML()


default_comment = f'''
Site configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class siteConfiguration(project):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    siteID: str
    siteName: str = None
    siteName: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None
    PI: str = None
    description: str = None

    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,'Sites',self.siteID,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveToYaml()

@dataclass(kw_only=True)
class site(baseFunctions):
    projectPath: str
    siteID: str
    config: siteConfiguration = None

    def __post_init__(self):
        self.config = siteConfiguration(projectPath=self.projectPath,siteID=self.siteID)
        super().__post_init__()
        type(self)
        
# # Template for multiple inheritance post init calls
# @dataclass(kw_only=True)
# class T1:
#     a: int = 1.1

#     def __post_init_T1__(self):
#         self.a=self.a*self.c

# @dataclass(kw_only=True)
# class T2:
#     b: str = 0

#     def __post_init_T2__(self):
#         self.b=self.b+.01

# @dataclass(kw_only=True)
# class T3(T1, T2):
#     c: float = 3.3

#     def __post_init__(self):
        
#         super().__post_init_T1__()
#         super().__post_init_T2__()
#         self.c*=self.b