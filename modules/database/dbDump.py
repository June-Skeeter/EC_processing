from modules.database.dataSource import dataSource#Configuration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
from modules.database.project import project
import numpy as np
import pandas as pd
import datetime
import os

# @dataclass(kw_only=True)
# class database(project):
#     subPath: str = 'Database'

@dataclass(kw_only=True)
class database(project):
    dbInterval: int = 1800 # seconds
    pythonTime: str = 'POSIX_Time_int64'
    matlabTime: str = 'clean_tv'
    siteID: str = None
    stageID: str = ''
    subPath: str = os.path.join('Database','yyyy','siteID','stageID')
    dfFolder: str = None
    dbFiles: list = None
    # dbData: dict = None

    def __post_init__(self):
        super().__post_init__()

    def setFolder(self,year,siteID=None,stageID=None):
        if siteID is None:
            siteID=self.siteID
        if stageID is None:
            stageID=self.stageID
        self.dbFolder = self.rootPath.replace('yyyy',str(year)).replace('siteID',siteID).replace('stageID',stageID)
        if not os.path.exists(self.dbFolder):
            self.logMessage(f'Creating new database folder: {os.path.abspath(self.dbFolder)}',verbose=True)
            os.makedirs(self.dbFolder,exist_ok=True)

        
    def readDbYear(self,year):
        self.setFolder(year)
        self.datetimeIndex = pd.DatetimeIndex(pd.date_range(
                    datetime.datetime(year,1,1,0,30),
                    datetime.datetime(year+1,1,1,0,0),
                    freq=str(self.dbInterval)+'s'))
        self.dbFiles = os.listdir(self.dbFolder)
        timestamp = ((self.datetimeIndex.astype(int)//1e9).values).astype('int64')
        datenum = timestamp.astype('float64')/86400.0+719529.0
        dbYear = pd.DataFrame(
                index=self.datetimeIndex,
                data={
                    self.pythonTime:timestamp,
                    self.matlabTime:datenum
                    }
            )
        if self.pythonTime not in self.dbFiles:
            timestamp.tofile(os.path.join(self.dbFolder,self.pythonTime))
            datenum.tofile(os.path.join(self.dbFolder,self.matlabTime))
        else:
            for f in self.dbFiles:
                if f not in [self.pythonTime,self.matlabTime]:
                    dbYear[f] = np.fromfile(os.path.join(self.dbFolder,f),dtype='float32')
        return(dbYear)

            
    def writeDbYear(self,dbYear):
        self.setFolder(dbYear.index[0].year)
        for col in dbYear.columns:
            if col not in [self.pythonTime,self.matlabTime]:
                dbYear[col].values.tofile(os.path.join(self.dbFolder,col))
        

@dataclass(kw_only=True)
class dbDump(database,dataSource):
    fileName: str
    overwrite: bool = False
    configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        self.logMessage(f'Writing: {self.fileName}',verbose=True)
        self.stageID = self.dataSourceID
        super().__post_init__()
        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileTemplate['fileFormat'],kwargs=self.sourceFileTemplate,verbose=self.verbose).parseFile()
        data.index=timestamp.datetime
        keep = [value['variableNameIn'] for value in self.sourceFileTemplate['dataColumns'].values() if not value['ignore']]
        data = data[keep]#.astype('float32')

        for year in data.index.year.unique():
            self.setFolder(year)
            dbYear = self.readDbYear(year)
            for col in data.columns:
                if self.overwrite:
                    self.logError('Option not yet implemented')
                else:
                    if col in dbYear.columns:
                        dbYear[col] = (dbYear[col].fillna(data[col])).astype('float32')
                    else:
                        dbYear[col] = np.nan
                        dbYear[col] = (dbYear[col].fillna(data[col])).astype('float32')
            self.writeDbYear(dbYear)
        # breakpoint()
        

                # else:

                # breakpoint()

            # self.dbYear(yyyy)
            # year = pd.DataFrame(
            #     index=pd.date_range(
            #         datetime.datetime(yyyy,1,1,0,30),
            #         datetime.datetime(yyyy+1,1,1,0,0),
            #         freq=str(self.dbInterval)+'s'),
            #     columns=data.columns,
            #     dtype='float32')
            # # year = year.astype(data.dtypes)
            # breakpoint()


        #Reset rootpath to save outputs to database location
        # self.subPath = self.subPath.replace('siteID',self.siteID).replace('dataSourceID',self.dataSourceID)
        # self.rootPath = os.path.join(self.projectPath,self.subPath)
        
        # self.writeBinaryFiles()

    # def writeBinaryFiles(self):
    #     data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileTemplate['fileFormat'],kwargs=self.sourceFileTemplate).parseFile()
    #     data.index=timestamp.datetime
    #     keep = [value['variableNameIn'] for value in self.sourceFileTemplate['dataColumns'].values() if not value['ignore']]
    #     data = data[keep].astype('float32')
    #     columns = data.columns
    #     # years = data.index.year.unique()  
    #     for yyyy in data.index.year.unique()  :
    #         # yd = data.loc[(data.index>=year.min())&(data.index<=year.max())].copy()
    #         breakpoint()
    #         year = pd.DataFrame(
    #             index=pd.date_range(datetime.datetime(yyyy,1,1,0,30),datetime.datetime(yyyy+1,1,1,0,0),freq=str(self.dbInterval)+'s'),
    #             columns=data.columns,dtype='float32')
    #         if self.overwrite:
    #             year = year.fillna(data)
    #         ydir = self.rootPath.replace('yyyy',str(yyyy))
    #         os.makedirs(ydir,exist_ok=True)
    #         if not os.path.isfile(os.path.join(ydir,self.pythonTime)):
    #             (year.index.astype(int)//1e9).astype('float32').values.tofile(os.path.join(ydir,self.pythonTime))
    #         for col in columns:
    #             fname = os.path.join(ydir,col)
    #             if os.path.isfile(fname):
    #                 if self.overwrite:
    #                     year[col].fillna(pd.Series(np.fromfile(fname,dtype='float32'),index=year.index))
    #                 else:
    #                     year[col] = np.fromfile(fname,dtype='float32')
    #             year[col] = year[col].fillna(data[col])
    #             year[col].values.tofile(fname)

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