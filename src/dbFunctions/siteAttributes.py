from .project import currentProject
# from ..helperFunctions.parseCoordinates import parseCoordinates
from dataclasses import dataclass, field
from ruamel.yaml import YAML
from datetime import datetime
import sys
import os

yaml = YAML()

@dataclass(kw_only=True)
class siteAttributes(currentProject):
    siteID: str = None
    siteName: str = None
    siteName: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None
    PI: str = None
    description: str = None

    def __post_init__(self):
        # Confirm project path is valid
        # Create one if valid path but no existing project
        self.pathCheck()

        baseAttributes = [k for k in self.__annotations__.keys() if self.__dataclass_fields__[k].repr]
        if self.siteID is None:
            self.logError("siteID must be provided")
        configPath = os.path.join(self.projectPath, 'Sites', self.siteID+'_metadata.yml')
        if not os.path.isfile(configPath):
            config = {'siteAttributes':{}}
        else:
            with open(configPath, 'r') as f:
                config = yaml.load(f)
                for key, value in config['siteAttributes'].items():
                    if key not in self.__annotations__.keys():
                        self.logWarning(f'Detected non-default attribute {key} in {self.siteID}{os.path.sep}siteAttributes.yml.',hold=True)
                        self.logWarning('If this is an important parameter, consider updating source code to make it a default.',fn=True)
                        setattr(self, key, value)
                        baseAttributes.append(key)
                    elif self.__dict__[key] is None:
                        setattr(self, key, value)
                    elif self.__dict__[key] != value:
                        self.logError(f'Discrepancy in attribute {key}: existing value {self.__dict__[key]}, new value {value}. Please resolve.')
        super().__post_init__()
        config['siteAttributes'] = {k: self.__dict__[k] for k in baseAttributes}
        with open(configPath, 'w') as f:
            yaml.dump(config, f)


        
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