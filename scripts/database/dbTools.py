# from scripts.database.dataSource import dataSource,dataSourceConfiguration
from dataclasses import dataclass, field
from scripts.database.project import project
# from submodules.helperFunctions.baseClass import baseClass
from submodules.helperFunctions.dictFuncs import packDict,unpackDict,updateDict
# from scripts.database.dbTrace import firstStageTrace
from scripts.database.site import site
# import matplotlib.pyplot as plt
from zoneinfo import ZoneInfo
import pandas as pd
import numpy as np
import datetime
import os

@dataclass(kw_only=True)
class database(project):
    dbPath: str = field(default = None,repr=False)
    updateConfig: bool = field(default = False,repr=False)

    def __post_init__(self):
        super().__post_init__()
        if not type(self).__name__.endswith('databaseConfiguration'):
            self.syncConfig(databaseConfiguration)
        
        if self.dbPath is None:
            self.dbPath = os.path.join(self.projectPath,self.subPath)

    def readSiteData(self,siteID,stageID,startYear=None,endYear=None):
        data = pd.DataFrame()
        stageID = os.path.normpath(stageID)
        dbFolders = unpackDict(self.dbMap)
        for year in self.dbMap:
            subPath = os.path.join(str(year),siteID,os.path.normpath(stageID))
            if subPath in dbFolders:
            # if (startYear is None or int(year) >= startYear) and (endYear is None or int(year) <= endYear) and siteID in self.dbMap[year] and stageID in unpackDict(self.dbMap[year][siteID]):
                data = pd.concat([data,self.readDbYear(year,siteID,stageID) ])
        return(data)
    
    def setFolder(self,year='',siteID='',stageID='',check=False):
        self.subPath = os.path.join(str(year),siteID,os.path.normpath(stageID))
        self.dbFolder = os.path.join(self.dbPath,self.subPath)    
        if not os.path.exists(self.dbFolder):
            self.logMessage(f'Creating new database folder: {os.path.abspath(self.dbFolder)}',verbose=True)
            os.makedirs(self.dbFolder,exist_ok=True)

    def readDbYear(self,year,siteID=None,stageID=None):
        self.setFolder(year,siteID,stageID)
        self.datetimeIndex = pd.DatetimeIndex(pd.date_range(
                    datetime.datetime(int(year),1,1,0,30),
                    datetime.datetime(int(year)+1,1,1,0,0),
                    freq=str(self.dbInterval)+'s'),
                    tz=ZoneInfo('UTC'))
        dbFiles = os.listdir(self.dbFolder)
        timestamp = ((self.datetimeIndex.astype(int)//1e9).values).astype('int64')
        datenum = timestamp.astype('float64')/86400.0+719529.0
        dbYear = pd.DataFrame(
                index=self.datetimeIndex,
                data={
                    self.pythonTime:timestamp,
                    self.matlabTime:datenum
                    }
            )
        
        if self.pythonTime not in dbFiles:
            timestamp.tofile(os.path.join(self.dbFolder,self.pythonTime))
            datenum.tofile(os.path.join(self.dbFolder,self.matlabTime))
        else:
            for f in dbFiles:
                if f not in [self.pythonTime,self.matlabTime]:
                    dbYear[f] = np.fromfile(os.path.join(self.dbFolder,f),dtype='float32')
        return(dbYear)
            
    def writeDataFrame(self,data,siteID,stageID,overwrite=False):
        if not isinstance(data.index,pd.DatetimeIndex):
            self.logWarning('datetime index required for writeDataFrame method')
            return('error')
        elif data.empty:
            self.logWarning('empty dataframe')
            return(False)
        for year in data.index.year.unique():
            dbYear = self.readDbYear(year,siteID,stageID)
            for col in data.columns:
                if overwrite:
                    self.logError('Option not yet implemented')
                else:
                    if col in dbYear.columns:
                        dbYear[col] = (dbYear[col].fillna(data[col])).astype('float32')
                    else:
                        dbYear[col] = np.nan
                        dbYear[col] = (dbYear[col].fillna(data[col])).astype('float32')
                
                dbYear[col].values.tofile(os.path.join(self.dbFolder,col))
            self.dbMap = updateDict(self.dbMap,packDict(self.subPath,fill=self.currentTimeString()))
            databaseConfiguration(projectPath=self.projectPath,dbMap=self.dbMap,readOnly=False)
        return(True)

        


@dataclass(kw_only=True)
class databaseConfiguration(database):
    dbInterval: int = 1800 # seconds
    pythonTime: str = 'POSIX_Time_int64'
    matlabTime: str = 'clean_tv'
    nYears: int = 0
    nSites: int = 0
    nSiteYears: int = 0
    dbMap: dict = field(default_factory=dict)
    fromFile: bool = field(default=True,repr=False)


    def __post_init__(self):
        self.configName = 'databaseConfiguration.yml'
        self.subPath = 'Database'

        super().__post_init__()
        self.stats()
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile()

    def stats(self):
        self.nYears = len(self.dbMap.keys())
        if self.nYears>0:
            self.nSites = set()
            for y in self.dbMap.values():
                sites = list(y.keys())
                self.nSites = self.nSites | set(sites)
                self.nSiteYears += len(sites)
            self.nSites = len(self.nSites)
# @dataclass(kw_only=True)
# class firstStage(database,site):
#     # siteID: str
#     subPath: str = os.path.join('Database','Calculation_Procedures','siteID','stageID')

#     def __post_init__(self):
#         super().__post_init__()
#         self.configName = f'{self.siteID}_firstStage.yml'

        
#         if not self.configFileExists or not self.readOnly:
#             print(self.configFileExists)
#             self.saveConfigFile()