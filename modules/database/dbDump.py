from modules.database.dataSource import dataSource#Configuration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
import pandas as pd
import datetime
import os


@dataclass(kw_only=True)
class dbDump(dataSource):
    fileName: str
    dbInterval: int = 1800 # seconds
    timestampName: str = 'POSIX_Time'
    configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        # self.subPath = os.path.sep.join(['configurationFiles',self.siteID,self.dataSourceID])
        super().__post_init__()
        #Reset rootpath to save outputs to database location
        self.subPath = os.path.sep.join(['Database','yyyy',self.siteID,self.dataSourceID])
        self.rootPath = os.path.join(self.projectPath,self.subPath)
        
        self.writeBinaryFiles()

    def writeBinaryFiles(self):
        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileTemplate['fileFormat'],kwargs=self.sourceFileTemplate).parseFile()
        data.index=timestamp.datetime
        keep = [value['variableNameIn'] for value in self.sourceFileTemplate['dataColumns'].values() if not value['ignore']]
        data = data[keep].astype('float32')
        years = data.index.year.unique()  
        for yyyy in years:
            year = pd.date_range(datetime.datetime(yyyy,1,1,0,30),datetime.datetime(yyyy+1,1,1,0,0),freq=str(self.dbInterval)+'s')
            ydir = self.rootPath.replace('yyyy',str(yyyy))
            os.makedirs(ydir,exist_ok=True)
            if not os.path.isfile(os.path.join(ydir,self.timestampName)):
                (year.astype(int)//1e9).astype('float32').values.tofile(os.path.join(ydir,self.timestampName))
                breakpoint()
        #     ix = timestamp.loc[timestamp['datetime'].dt.year==year].index
        # breakpoint()
        


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