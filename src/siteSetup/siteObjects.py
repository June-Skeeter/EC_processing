import os
from typing import Iterable
from datetime import datetime, timezone
import dataclasses
from dataclasses import dataclass, field, make_dataclass

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
# from modules.helperFunctions.getClasses import getClasses

from src.databaseObjects.defaultObjects import spatialObject

# import src.siteSetup.loggerObjects as loggerObjects
import src.databaseObjects.defaultObjects as defaultObjects
from src.siteSetup.ecSystem import ecSystem
from src.siteSetup.biometSystem import biometSystem

# # Get all defined loggers
# import src.readData.dataSource as dataSource
# dataSource = getClasses(dataSource)
# dataSource = {cl.__name__:cl for cl in dataSource[::-1]}

# # Get all defined sensors
# import src.siteSetup.sensorObjects as sensorObjects
# sensorObjects = getClasses(sensorObjects)
# sensorObjects = {cl.__name__:cl for cl in sensorObjects[::-1]}


@dataclass(kw_only=True)
class siteObject(spatialObject):
    projectPath: str = field(default=None,repr=False)
    validate: bool = field(
        repr=False,
        default=True
    )
    siteID: str = field(
        default = 'siteID',
        metadata = {'description': 'Unique Site Identifier'} 
    )
    siteName: str = field(
        default = None,
        metadata = {'description': 'Name of the Site'} 
    )
    description: str = field(
        default = None,
        metadata = {'description': 'self explanatory'} 
    )
    PI: str = field(
        default = None,
        metadata = {'description': 'Principal Investigator(s)'} 
    )
    ecSystems: Iterable = field(
        default_factory=dict,
    )
    # chamberSystems: Iterable = field(
    #     default_factory=dict,
    # )
    biometSystems: Iterable = field(
        default_factory=dict,
    )


    def __post_init__(self):

        # for key in self.__annotations__:
        #     if key.endswith('Systems'):
        #         setattr(self,key,self.formatClassIterables(getattr(self,key)))
        if self.projectPath:
            self.configFile = os.path.join(self.projectPath,self.siteID,type(self).__name__+'.yml')
        super().__post_init__()
        self.ecSystems = self.processClassIterable(self.ecSystems,ecSystem)
        self.biometSystems = self.processClassIterable(self.biometSystems,biometSystem)
        if self.validate:
            self.saveConfigFile()
        

# @dataclass(kw_only=True)
# class Chamber(defaultObjects.siteObject):
#     pass

# @dataclass(kw_only=True)
# class siteMetadata(spatialObject):
#     projectPath: str = field(default=None,repr=False)
#     validate: bool = field(
#         repr=False,
#         default=True
#     )
#     siteID: str = field(
#         default = 'siteID',
#         metadata = {'description': 'Unique Site Identifier'} 
#     )
#     siteName: str = field(
#         default = None,
#         metadata = {'description': 'Name of the Site'} 
#     )
#     description: str = field(
#         default = None,
#         metadata = {'description': 'self explanatory'} 
#     )
#     PI: str = field(
#         default = None,
#         metadata = {'description': 'Principal Investigator(s)'} 
#     )
#     systems: Iterable = field(
#         default_factory=list,
#     )
#     # dataLoggers: Iterable = field(
#     #     default_factory=dict,
#     #     metadata = {
#     #         'description': 'Inventory of data sources for site',
#     #         # 'options':{name:value.template() for name,value in dataSource.items()}
#     # })
#     # dataSources: Iterable = field(
#     #     default_factory = dict,
#     #     metadata = {
#     #         'description': 'Inventory of data sources for site',
#     #         'options':{name:value.template() for name,value in dataSource.items()}
#     # })

#     def __post_init__(self):
#         self.UID = self.siteID
#         if self.projectPath:
#             self.configFile = os.path.join(self.projectPath,self.siteID,type(self).__name__+'.yml')
#         super().__post_init__()
#         if self.validate:
#             self.dataLoggers = self.parseLoggers()
#             self.saveConfigFile(inheritance=True)
    
#     def parseLoggers(self):
#         cleanLoggers = {}
#         if type(self.dataLoggers) is dict:
#             self.dataLoggers = list(self.dataLoggers.values())
#         for obj in self.dataLoggers:
#             if dataclasses.is_dataclass(obj):
#                 obj = dcToDict(obj,repr=True,inheritance=True)
#             if 'loggerModel' not in obj or not hasattr(loggerObjects,obj['loggerModel']):
#                 self.logError(f'Not a valid loggerObject: {obj}')
#             else:
#                 kwargs = obj
#                 logger = getattr(loggerObjects,obj['loggerModel'])
#                 logger = logger.from_dict(kwargs)
#                 while logger.loggerID in cleanLoggers.keys():
#                     logger.updateUID()
#                 cleanLoggers[logger.loggerID] = dcToDict(logger,inheritance=False)|dcToDict(logger,keepNull=False)
#         return(cleanLoggers)



@dataclass(kw_only=True)
class getSite(project):
    siteID: str
    siteMetadata: dict = field(init=False)

    def __post_init__(self):
        cfg = os.path.join(self.projectPath,self.siteID,'siteMetadata.yml')
        self.siteMetadata = siteMetadata(configFile=cfg,siteID=self.siteID,validate=False).config()
        