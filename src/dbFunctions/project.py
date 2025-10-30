import os
import sys
import yaml
from datetime import datetime, UTC

from dataclasses import dataclass, field
from ..helperFunctions.baseFunctions import baseFunctions
# from ..helperFunctions.dictFuncs import dcToDict,loadDict,saveDict

default_comment = f'''
Database project configuration file
Created: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

# 
@dataclass(kw_only=True)
class projectConfiguration(baseFunctions):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    projectPath: str = None
    dateCreated: str = None
    dateModified: str = field(default_factory=lambda: datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'))
    siteIDs: list = field(default_factory=lambda:['__TEMPLATE__'])

    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveToYaml()

    # def save(self):
    #     saveDict(
    #         dcToDict(self,repr=True,inheritance=False),
    #         fileName=self.fileName,
    #         header=self.header
    #     )

        # os.makedirs(self.projectPath,exist_ok=True)
        # fn = os.path.join(self.projectPath,type(self).__name__+'.yml')
        # print(dcToDict(self,onlyChild=True))
        # with open(fn,'w') as f:
        #     yaml.safe_dump({key:self.__dict__[key] for key in self.__annotations__},f)

@dataclass(kw_only=True)
class project(baseFunctions):
    projectPath: str
    config: projectConfiguration = None

    def __post_init__(self):
        self.config = projectConfiguration(projectPath=self.projectPath)
        super().__post_init__()
        # print(hasattr(self,'siteID'))

# @dataclass(kw_only=True)
# class currentProject(typeEnforcer):
#     projectPath: str
#     config = {}
#     databaseInterval: int = 1800 # in seconds
#     currentTime: str = field(default_factory=lambda: datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ'))
#     safeMode: bool = True # If True, prevents overwriting existing files without warning.
#     siteList: list = field(default_factory=list)

#     def __post_init__(self):
#         self.readConfig()
        
#         # self.configFileName = os.path.join(self.projectPath,self.configFileName)
#         # if not os.path.isdir(self.projectPath) or os.listdir(self.projectPath)==[]:
#         #     # os.makedirs(self.projectPath, exist_ok=True)
#         #     os.makedirs(os.path.join(self.projectPath,'Sites'), exist_ok=True)
#         #     with open(self.configFileName,'w') as f:
#         #         f.write('# A test comment\n# All comments before the tripple dash will be preserved unchnaged'+startMarker)
#         #         yaml.safe_dump({'creationDate':self.currentTime,'lastModified':self.currentTime,'siteList':[]},f)
#         # elif not os.path.isfile(self.configFileName):
#         #     self.logError(f'Database path {self.projectPath} exists but is missing {self.configFileName} file. Please check.')

#         # with open(self.configFileName) as f:
#         #     self.configHeader = f.read().split(startMarker)[0]
#         # with open(self.configFileName) as f:
#         #     self.config = yaml.safe_load(f)
#         # print(self.config)
        
#         print(self.__class__.__name__,'!!!!!!!!!!!!!!!')
    
#     def close(self):
#         self.config['lastModified'] = self.currentTime
#         with open(self.configFileName,'w') as f:
#             f.write(self.configHeader+startMarker)
#             yaml.safe_dump(self.config,f)

# class newProject(currentProject):

#     def __post_init__(self):
#         super().__post_init__()
#         self.close()
#         # self.pathCheck(siteID='Template')
#         # for c in (self.__class__.__mro__[:-1]):
#         #     print(c.__name__)
#         #     print(c.__annotations__)
#         # print(self.__class__.__name__)

