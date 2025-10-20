from ..dbFunctions.project import project
from dataclasses import dataclass, field
from ruamel.yaml import YAML
from datetime import datetime
import sys
import os

yaml = YAML()

@dataclass(kw_only=True)
class measurementAttributes:
    measurementID: str = None
    measurementType: str = None
    samplingFrequency: float = None  # in Hz
    samplingInterval: float = None # in seconds

    def __post_init__(self):
        if self.samplingInterval is not None:
            self.samplingFrequency = 1.0 / self.samplingInterval

@dataclass(kw_only=True)
class siteAttributes(project,measurementAttributes):
    siteID: str = None
    siteName: str = None
    latitude: float = None
    longitude: float = None

    def __post_init__(self):
        baseAttributes = [k for k in list(siteAttributes.__dict__.keys()) if k in self.__dataclass_fields__.keys()]
        if self.siteID is None:
            sys.exit("siteID must be included for siteAttributes.")
        self.pathCheck()
        configPath = os.path.join(self.projectPath, 'Sites', f'{self.siteID}_siteAttributes.yml')
        if os.path.isfile(configPath):
            with open(configPath, 'r') as f:
                existing_attrs = yaml.load(f)
                for key, value in existing_attrs.items():
                    if self.__dict__[key] is None:
                        setattr(self, key, value)
                    elif key not in baseAttributes:
                        print(f'Warning: Adding new, non-default attribute {key} for siteID {self.siteID}.')
                        setattr(self, key, value)
                        baseAttributes.append(key)
                    elif self.__dict__[key] != value:
                        sys.exit(f'Discrepancy found attribute {key}: existing value {self.__dict__[key]}, new value {value}. Please resolve.')
        with open(configPath, 'w') as f:
            yaml.dump({k: self.__dict__[k] for k in baseAttributes}, f)
                

        if self.measurementType is not None:
            super().__post_init__()
        

        


        
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