# from typing import Iterable
from dataclasses import dataclass, field, MISSING

# from modules.helperFunctions.getClasses import getClasses
from src.databaseObjects.project import project
from src.siteSetup.siteObjects import siteObject

@dataclass(kw_only=True)
class dataSource(project):
    siteID: str
    siteConfig: dict = field(init=False)
    sourceType: str = None
    
    def __post_init__(self):
        super().__post_init__()
        self.siteConfig = siteObject(
            projectPath = self.projectPath,
            projectConfig = self.projectConfig,
            siteID = self.siteID,
            safeMode = True
            )

# from src.databaseObjects.defaultObjects import spatialObject

# # Get all defined sensors
# import src.siteSetup.sensorObjects as sensorObjects
# sensorObjects = getClasses(sensorObjects)
# sensorObjects = {cl.__name__:cl for cl in sensorObjects[::-1]}

# @dataclass(kw_only=True)
# class dataSource(spatialObject):
#     sourceID: str = field(default=None,init=False)
#     sourceType: str = field(
#         init = False,
#         metadata={
#             'description':'Type of data source',
#         }
#     )
#     fileType: str = field(
#         metadata={
#             'description': 'type of file associated with the input data source',
#         }
#     )
#     sourceFiles: dict = field(
#         default_factory=dict,
#         init=False,
#         repr=False
#     )

#     def __post_init__(self):
#         if not hasattr(self,'sourceID'):
#             self.sourceID = type(self).__name__
#         super().__post_init__()

# @dataclass(kw_only=True)
# class manualMeasurement(dataSource):
#     sourceType: str = 'manualMeasurement'
#     description: str = None
#     fileType: str = 'csv'

# @dataclass(kw_only=True)
# class externalMeasurement(dataSource):
#     sourceType: str = 'externalMeasurement'
#     description: str = None
#     fileType: str = 'csv'


    
# @dataclass(kw_only=True)
# class dataLogger(dataSource):
#     sourceType: str = 'dataLogger'
#     loggerModel: str = field(
#         init=False,
#         metadata = {
#             'description': 'The model of data logger, auto-filled from class name',
#     })
#     manufacturer: str = field(
#         default = None,
#         init=False,
#         metadata = {
#             'description': 'Indicates manufacturer of sensor, auto from class name',
#     })
#     serialNumber: str = field(
#         default = None,
#         metadata = {
#             'description': 'Serial# (if known)',
#     })
#     sensorInventory: Iterable = field(
#         default_factory=lambda:[sensorObjects['genericSensor']()],
#         metadata={
#             'description':'Inventory of sensors linked to the logger',
#             'options':{name:value.template() for name,value in sensorObjects.items()}
#             })

#     def __post_init__(self):
#         if not hasattr(self,'loggerModel'):
#             self.loggerModel = type(self).__name__
#         if not hasattr(self,'sourceID'):
#             self.sourceID = self.loggerModel
#         if self.serialNumber:
#             self.sourceID = f"{self.sourceID}_{self.serialNumber}"
#         self.UID = self.loggerModel
#         breakpoint()
#         self.nestedClasses = sensorObjects
#         self.sensorInventory = self.parseNestedObjects(
#             objectsToParse = self.sensorInventory,
#             objectOptions = sensorObjects,
#             objectID = 'loggerModel')
#         super().__post_init__()

# # @dataclass
# # class HOBO(dataLogger):
# #     manufacturer: str = 'Onset'
# #     fileType: str = 'csv'