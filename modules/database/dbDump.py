from modules.database.dataSource import dataSource#Configuration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
from modules.database.project import project
import numpy as np
import pandas as pd
import datetime
import os

@dataclass(kw_only=True)
class database(project):
    dbInterval: int = 1800 # seconds
    timestampName: str = 'POSIX_Time'
    subPath: str = os.path.join('Database','yyyy','siteID')


    def dbPath(self,yyyy,stageID='',varName=''):
        rootPath = self.rootPath.replace('yyyy',str(yyyy)).replace('siteID',self.siteID)
        return(os.path.join(rootPath,stageID,varName))
    
    # def readTrace(self,):

    # def readDbYear(self,year):

    # def writeDbYear(self,year,data):

@dataclass(kw_only=True)
class dbDump(database,dataSource):
    fileName: str
    overwrite: bool = False
    configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        super().__post_init__()


        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileTemplate['fileFormat'],kwargs=self.sourceFileTemplate).parseFile()
        data.index=timestamp.datetime
        keep = [value['variableNameIn'] for value in self.sourceFileTemplate['dataColumns'].values() if not value['ignore']]
        data = data[keep]#.astype('float32')

        for yyyy in data.index.year.unique():
            
            year = pd.DataFrame(index=pd.date_range(datetime.datetime(yyyy,1,1,0,30),datetime.datetime(yyyy+1,1,1,0,0),freq=str(self.dbInterval)+'s'), columns=data.columns)
            # year = year.astype(data.dtypes)
            breakpoint()


        #Reset rootpath to save outputs to database location
        # self.subPath = self.subPath.replace('siteID',self.siteID).replace('dataSourceID',self.dataSourceID)
        # self.rootPath = os.path.join(self.projectPath,self.subPath)
        
        # self.writeBinaryFiles()

    def writeBinaryFiles(self):
        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileTemplate['fileFormat'],kwargs=self.sourceFileTemplate).parseFile()
        data.index=timestamp.datetime
        keep = [value['variableNameIn'] for value in self.sourceFileTemplate['dataColumns'].values() if not value['ignore']]
        data = data[keep].astype('float32')
        columns = data.columns
        # years = data.index.year.unique()  
        for yyyy in data.index.year.unique()  :
            # yd = data.loc[(data.index>=year.min())&(data.index<=year.max())].copy()
            breakpoint()
            year = pd.DataFrame(
                index=pd.date_range(datetime.datetime(yyyy,1,1,0,30),datetime.datetime(yyyy+1,1,1,0,0),freq=str(self.dbInterval)+'s'),
                columns=data.columns,dtype='float32')
            if self.overwrite:
                year = year.fillna(data)
            ydir = self.rootPath.replace('yyyy',str(yyyy))
            os.makedirs(ydir,exist_ok=True)
            if not os.path.isfile(os.path.join(ydir,self.timestampName)):
                (year.index.astype(int)//1e9).astype('float32').values.tofile(os.path.join(ydir,self.timestampName))
            for col in columns:
                fname = os.path.join(ydir,col)
                if os.path.isfile(fname):
                    if self.overwrite:
                        year[col].fillna(pd.Series(np.fromfile(fname,dtype='float32'),index=year.index))
                    else:
                        year[col] = np.fromfile(fname,dtype='float32')
                year[col] = year[col].fillna(data[col])
                year[col].values.tofile(fname)

            # for col 
            # for col in yd.columns:
            #     print(yd[col])

        


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