import os
import sys
from .project import project
# from ..helperFunctions.parseCoordinates import parseCoordinates
from dataclasses import dataclass, field
# from ruamel.yaml import YAML
from datetime import datetime, UTC
from ..helperFunctions.baseFunctions import baseFunctions

# yaml = YAML()


default_comment = f'''
Site configuration file
Created: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}
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



        # baseAttributes = [k for k in self.__annotations__.keys() if self.__dataclass_fields__[k].repr]
        # if self.siteID is None:
        #     self.logError("siteID must be provided")
        # configPath = os.path.join(self.projectPath, 'Sites', self.siteID+'_metadata.yml')
        # if not os.path.isfile(configPath):
        #     config = {'siteConfiguration':{}}
        # else:
        #     with open(configPath, 'r') as f:
        #         config = yaml.load(f)
        #         for key, value in config['siteConfiguration'].items():
        #             if key not in self.__annotations__.keys():
        #                 self.logWarning(f'Detected non-default attribute {key} in {self.siteID}{os.path.sep}siteConfiguration.yml.',hold=True)
        #                 self.logWarning('If this is an important parameter, consider updating source code to make it a default.',fn=True)
        #                 setattr(self, key, value)
        #                 baseAttributes.append(key)
        #             elif self.__dict__[key] is None:
        #                 setattr(self, key, value)
        #             elif self.__dict__[key] != value:
        #                 self.logError(f'Discrepancy in attribute {key}: existing value {self.__dict__[key]}, new value {value}. Please resolve.')
        # super().__post_init__()
        # config['siteConfiguration'] = {k: self.__dict__[k] for k in baseAttributes}
        # with open(configPath, 'w') as f:
        #     yaml.dump(config, f)


        
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