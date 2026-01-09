from modules.database.dataSource import dataSource#Configuration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
import os


@dataclass(kw_only=True)
class dbDump(dataSource):
    fileName: str
    configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        # self.subPath = os.path.sep.join(['configurationFiles',self.siteID,self.dataSourceID])
        super().__post_init__()
        #Reset rootpath to save outputs to database location
        self.subPath = os.path.sep.join(['Database',self.siteID,self.dataSourceID])
        self.rootPath = os.path.join(self.projectPath,self.subPath)


# @dataclass(kw_only=True)
# class dbDump(dataSource):
#     # siteID: str
#     # dataSourceID: str
#     fileName: str
#     # template: dict = field(default_factory=lambda:metadataMap)
#     metadataFile: dict = field(default_factory=dict)
#     f32Files: list = field(default_factory=list)
#     eddyproFile: dict = field(default_factory=dict)
#     defaultInterval: int = 30
#     integratedSonics: list = field(default_factory=lambda:['IRGASON'])
#     configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

#     def __post_init__(self):
#         # self.subPath = os.path.sep.join(['configurationFiles',self.siteID,self.dataSourceID])

#         # T1 = time.time()
#         super().__post_init__()
#         breakpoint()