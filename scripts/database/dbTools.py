from modules.database.dataSource import dataSource,dataSourceConfiguration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
from modules.database.project import project
from modules.helperFunctions.baseClass import baseClass
from modules.database.dbTrace import firstStageTrace
from modules.database.site import site
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
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
                    freq=str(self.dbInterval)+'s'),
                    tz=ZoneInfo(self.timezone))
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
    overwrite: bool = field(default=False,repr=False)
    # configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        self.logMessage(f'Writing: {self.fileName}',verbose=True)
        # else:
        #     self.stageID = os.path.join(self.stageID,self.dataSourceID)
        super().__post_init__()
        if self.stageID == '':
            self.stageID = os.path.join(self.measurementType,self.dataSourceID)
        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileMetadata['fileFormat'],kwargs=self.sourceFileMetadata,verbose=self.verbose).parseFile()
        data.index=timestamp.datetime
        
        if self.timezone is not None:
            data.index = data.index.tz_localize(self.timezone)
        keep = [value['originalVariable'] for value in self.sourceFileMetadata['traceMetadata'].values() if not value['ignore']]
        data = data[keep]
        print(data.shape)

        update = False
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
                
                # update dateRange as relevant
                ix = dbYear[~dbYear[col].isna()].index
                dr = self.sourceFileMetadata['traceMetadata'][col]['dateRange']
                if len(dr) == 0:
                    self.sourceFileMetadata['traceMetadata'][col]['dateRange'] = [ix.min().to_pydatetime(),ix.max().to_pydatetime()]
                    update = True
                else:
                    if self.sourceFileMetadata['traceMetadata'][col]['dateRange'][0]>ix.min():
                        self.sourceFileMetadata['traceMetadata'][col]['dateRange'][0]=ix.min().to_pydatetime()
                        update = True
                        
                    if self.sourceFileMetadata['traceMetadata'][col]['dateRange'][1]<ix.max():
                        self.sourceFileMetadata['traceMetadata'][col]['dateRange'][1]=ix.max().to_pydatetime()
                        update = True
            self.writeDbYear(dbYear)
        if update:
            dataSourceConfiguration.from_class(self,{'readOnly':False,'projectPath':self.projectPath})
    #     self.firstStageIni()
        firstStage(siteID=self.siteID)

    # def firstStageIni(self):
    #     Traces = {}
    #     for key,value in self.sourceFileMetadata['traceMetadata'].items():
    #         kwargs = value
    #         kwargs['inputFileName'] = value['fileName']
    #         kwargs['inputFileName_dates'] = value['dateRange']
    #         Traces[value['variableName']] = firstStageTrace.from_dict(kwargs).to_dict()
    #     breakpoint()

@dataclass(kw_only=True)
class firstStage(database,site):
    # siteID: str
    subPath: str = os.path.join('Database','Calculation_Procedures','siteID','stageID')

    def __post_init__(self):
        super().__post_init__()
        self.configName = f'{self.siteID}_firstStage.yml'

        
        if not self.configFileExists or not self.readOnly:
            print(self.configFileExists)
            self.saveConfigFile()