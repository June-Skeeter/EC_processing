from modules.database.dataSource import dataSource#Configuration
from modules.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
from modules.database.project import project
from modules.helperFunctions.baseClass import baseClass
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
        # else:
        #     self.stageID = os.path.join(self.stageID,self.dataSourceID)
        super().__post_init__()
        if self.stageID == '':
            self.stageID = os.path.join(self.sourceType,self.dataSourceID)
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

@dataclass(kw_only=True)
class firstStageTrace:
    variableName: str = field(default='', metadata={'description':'defaults to inputFileName, change to output as a different filename'})
    title: str = field(default='', metadata={'description':''})
    units: str = field(default='', metadata={'description':''})

    
    inputFileName: str = field(metadata={'description':'name of the raw input file'})
    instrumentType: str = field(default='', metadata={'description':''})
    measurementType: str = field(metadata={'description':'taken from sourceType variable'})
    minMax: list = field(default_factory=list, metadata={'description':'optional to set min/max clipping'})
    zeroPt: list = field(default_factory=lambda:[-9999], metadata={'description':'default NaN value (not actually zero)'})
    # Required for second stage
#     variableName: str = None
#     title: str = ''
#     units: str = ''
#     inputFileName: str
#     instrumentType: str = ''
#     measurementType: str = ''
#     minMax: list = field(default_factory=lambda:[-np.inf,np.inf])
#     Overwrite: int = 0
#     dependent: int = ''
#     inputFileName_dates: list = field(default_factory=list)
#     instrument: str = ''
#     instrumentSN: list = field(default_factory=list)
#     loggedCalibration: list = field(default_factory=list)
#     currentCalibration: list = field(default_factory=list)
#     comments: str = ''
#     zeroPt: float = -9999


@dataclass(kw_only=True)
class Trace:
    # The expected fields and their corresponding types for a trace object
    # metadata field instructs behavior
    # Standard T/F (True for all parameter defined by default, False for non-standard parameters parsed from ini)
    # Stage controls which parameters are written:
    #   * common > always written
    #   * firststage > always written (for first stage)
    #   * secondstage > always written (for second stage)
    #       * optional only written if provided

    # Required for all 
    variableName: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':False})
    title: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':None})
    units: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':None})
    # Required for first stage
    inputFileName: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False}) # Note, can be a list instead if needed?  matlab codebase has variable as cell array but not sure why?
    instrumentType: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
    measurementType: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
    minMax: list = field(default_factory=list, metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
    zeroPt: list = field(default_factory=lambda:[-9999], metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
    # Required for second stage
    Evaluate: str = field(default='', metadata={'standard':True,'optional':False,'stage':'secondstage','literal':True})
    # Optional parameters
    # ONLY required for optionals we want to have predefined settings
    # Can take any non-defined field, but defining here will give defaults for standardization
    Overwrite: int = field(default=0, metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
    dependent: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
    originalVariable: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':True})
    postEvaluate: str = field(default='', metadata={'standard':True,'optional':True,'stage':'secondstage','literal':True})
    comment: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':True})
    ECCC_station: str = field(default='', metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
    inputFileName_dates: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
    
    # Hidden (parameters to control behaviour which will not be written)
    # by default, repr should be true, but when setting globals trace-by-trace, will set to false
    repr: bool = field(default=True,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
    stage: str = field(default='firststage',repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
    fields_on_the_fly: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
    verbose: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
    # If file being parsed is an include,
    # Use variable substitution for globalVariables instead of anchors (limited to within one-file)
    include: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})



@dataclass(kw_only=True)
class firstStageIni(baseClass):
    siteID: str = field(repr=False)
    Metadata: dict = field(default_factory=dict)
    globalVars: dict = field(default_factory=dict)
    Trace: dict = field(default_factory=dict)
    Include: dict = field(default_factory=dict)


