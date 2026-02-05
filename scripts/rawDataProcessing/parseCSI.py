# Reads campbell scientific .dat files in TOA5, TOB3, and mixed array (not yet supported) formats

from dataclasses import dataclass,field
from collections import defaultdict
from submodules.helperFunctions.parseFrequency import parseFrequency
from submodules.helperFunctions.dictFuncs import updateDict
from scripts.rawDataProcessing.rawFile import sourceFile
import scripts.database.dataLoggers as dataLoggers
from scripts.database.dbTrace import rawTrace
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pandas as pd
import os
from datetime import datetime
from typing import Iterable
import numpy as np
import struct
import sys
import re

# from src.siteSetup.siteObjects import siteObject
# from src.readData.dataSource import dataSource
# from src.databaseObjects.defaultObjects import sourceObject

@dataclass
class csiType:
    filepath: str
    fileType: str = field(init=False)

    def __post_init__(self):
        if not os.path.isfile(self.filepath):
            self.logError('Invalid filepath')
        else:
            with open(self.filepath,'rb') as f:
                l = f.readline()
                self.fileType = l.decode('ascii').strip().replace('"','').split(',')[0]
            if len(self.fileType) == 3 and int(self.fileType):
                self.fileType = 'MixedArray'


@dataclass(kw_only=True)
class csiTrace(rawTrace):
    defaultTypes = defaultdict(lambda: '<f4',RECORD ='<u4',TIMESTAMP = 'string') # Does not apply to TOB3 which have type specified in header
    csiTypeMap = {
        'FP2':{'struct':'H','output':'<f4'},
        'IEEE4B':{'struct':'f','output':'<f4'},
        'IEEE8B':{'struct':'d','output':'<f8'},
        'LONG':{'struct':'l','output':'<i8'},
        'INT4':{'struct':'i','output':'<i4'},
        'ASCII':{'struct':'s','output':'string'},
    }
    byteMap: str = field(init=False)

    def __post_init__(self):
        self.ignoreByDefault =  ['RECORD','TIMESTAMP','POSIX_Time','NANOSECONDS']#,'POSIX_Time','NANOSECONDS']
        if self.dtype is None:
            self.dtype = self.defaultTypes[self.variableName]
        elif self.dtype in self.csiTypeMap:
            self.byteMap = self.csiTypeMap[self.dtype]['struct']
            self.dtype = self.csiTypeMap[self.dtype]['output']
        elif type(self.dtype) is str and self.dtype.startswith('ASCII'):
            self.byteMap = self.dtype.strip('ASCII()') + self.csiTypeMap['ASCII']['struct']
            self.dtype = self.csiTypeMap['ASCII']['output']
        if self.variableName == 'TIMESTAMP':
            self.units = 'datetime'
            # self.dtype = '<i8'
        if type(self.dtype) != str:
            self.dtype = self.dtype.str
        if self.dtype == 'string':
            self.ignore = True
        super().__post_init__()

@dataclass(kw_only=True)
class csiFile(sourceFile):
    # Some files may contain multiple tables
    # Attributes common to a given file
    fileObject: object = field(default=None,repr=False,init=False)
    dataLogger: dict = field(default_factory=dict,repr=False,init=False)
    stationName: str = None
    loggerModel: str = None
    serialNumber: str = None
    program: str = None
    fileTimestamp: datetime = field(repr=False,init=False)
    campbellBaseTime: float = field(
        default=631152000.0,
        repr=False,
        init=False,
        metadata={
            'description':'Start of CSI epoch in POSIX epoch: pd.to_datetime("1990-01-01").timestamp()'
            })
    
    def __post_init__(self):
        super().__post_init__()
        self.processFile()
        if self.loggerModel is None and self.extractData:
            pass
        elif hasattr(dataLoggers,self.loggerModel):
            logger = getattr(dataLoggers,self.loggerModel)
            self.dataLogger = logger(
                stationName=self.stationName,
                serialNumber=self.serialNumber,
                ).to_dict(keepNull=False)
        else:
            self.logError('Could not identify logger')
        
    
@dataclass(kw_only=True)
class csiTable(csiFile):
    # Attributes common to a CSI format datable
    asciiHeader: list = field(init=False,repr=False)
    nLinesAsciiHeader: int = field(repr=False)
    tableName: str = None
    timestampName: str = field(default='TIMESTAMP',init=False,repr=False)
    recordName: str = field(default='RECORD',init=False,repr=False)
    samplingInterval: float = field(default=None,init=None)  # in seconds
    samplingFrequency: str = field(default=None,init=None) # in Hz
    gpsDriftCorrection: bool = field(default=False,repr=False,metadata={'description':'Consider using for high frequency data if GPS clock resets were enabled.  This clock correction is useful to ensure long-term stability of the data logger clock but causes problems when splitting high-frequency data files.  Assuming the file does not span more than a day, the drift should be minimal, so we can "remove" the offset within a file to ensure timestamps are sequential'})
    mode: str = field(default='r',repr=False)

    def __post_init__(self):
        if self.nLinesAsciiHeader > 0:
            if self.fileFormat == 'TOB3':
                with open(self.fileName, self.mode) as self.fileObject:
                    self.asciiHeader = [self.readAsciiLine(self.fileObject.readline()) for l in range(self.nLinesAsciiHeader)]
            else:
                with open(self.fileName, self.mode) as self.fileObject:
                    self.asciiHeader = [self.readAsciiLine(self.fileObject.readline()) for l in range(self.nLinesAsciiHeader)]
            if self.fileFormat != self.asciiHeader[0][0]:
                self.logError(f"{self.fileName} is not in {self.fileFormat} format")
            self.stationName=self.asciiHeader[0][1]
            self.loggerModel=self.asciiHeader[0][2]
            self.serialNumber=self.asciiHeader[0][3]
            self.program=self.asciiHeader[0][5]
        super().__post_init__()
    
    def readAsciiLine(self,line):
        if type(line) == str:
            return(line.strip().replace('"','').split(','))
        else:
            return(line.decode('ascii').strip().replace('"','').split(','))
        
    def finishTable(self):
        self.datetimeTrace = pd.DataFrame()
        if 'self.timestampName' in self.dataTable.columns and is_datetime(self.dataTable[self.timestampName]):
            self.datetimeTrace['datetime'] = self.dataTable[self.timestampName]
        elif is_datetime(self.dataTable.index):
            self.datetimeTrace['datetime'] = self.dataTable.index
        else:
            self.datetimeTrace['datetime'] = pd.to_datetime((self.dataTable['POSIX_Time']*1e9).astype('int64')+self.dataTable['NANOSECONDS'],unit='ns') 
        if self.gpsDriftCorrection:
            # Identify gaps in time series
            Offset = (self.dataTable[self.timestampName].diff().fillna(self.samplingInterval)-self.samplingInterval).cumsum()
            self.dataTable[self.timestampName] -= Offset
            if self.verbose:
                self.logMessage(f"Total GPS induced offset in {self.fileName} is {Offset.iloc[-1]}s",verbose=False)
        
@dataclass(kw_only=True)
class TOA5(csiTable):
    nLinesAsciiHeader: int = field(default=4,repr=False,init=False)
    fileFormat: str = 'TOA5'
        
    def processFile(self):
        #First read metadata from files header
        self.fileTimestamp = datetime.strptime(re.search(r'([0-9]{4}\_[0-9]{2}\_[0-9]{2}\_[0-9]{4})', self.fileName.rsplit('.',1)[0]).group(0),'%Y_%m_%d_%H%M')
        self.tableName = self.asciiHeader[0][-1]
    
        # get preview if not extracting all data
        if self.extractData:
            nrows = None
        else:
            nrows = 30
        self.dataTable = pd.read_csv(
            self.fileName,
            skiprows=[0,2,3],
            header=[0],
            parse_dates=[self.timestampName],
            date_format='ISO8601',
            dtype=csiTrace.defaultTypes,
            nrows=nrows
            )
        # Extract metadata for each variable
        self.traceMetadata =  {
            columnName:csiTrace(originalVariable=columnName,units=units,operation=operation,dtype=dtype,traceMetadata=self.traceMetadata).to_dict(keepNull=False)
                for columnName,units,operation,dtype in 
                zip(self.asciiHeader[1],self.asciiHeader[2],self.asciiHeader[3],list(self.dataTable.dtypes))}
        self.samplingInterval = self.dataTable.TIMESTAMP.diff().median().total_seconds()
        self.samplingFrequency = (1.0 / self.samplingInterval)
        self.finishTable()


@dataclass(kw_only=True)
class TOB3(csiTable):
    timestampName: list = field(default_factory=lambda:['POSIX_Time','NANOSECONDS'],init=False,repr=False)
    nLinesAsciiHeader: int = field(default=6,repr=False,init=False)
    headerSize: int = field(default=12,repr=False,init=False)
    footerSize: int = field(default=4,repr=False,init=False)
    byteMap: str = field(repr=False,init=False)
    fileFormat: str = 'TOB3'
    mode: str = field(default='rb',repr=False)
        
    def processFile(self):
        #First read metadata from files header
        self.fileSize = os.path.getsize(self.fileName)
        with open(self.fileName,self.mode) as self.fileObject:
            for _ in range(self.nLinesAsciiHeader):
                next(self.fileObject)
            self.fileTimestamp = pd.to_datetime(self.asciiHeader[0][-1])
            self.tableName = self.asciiHeader[1][0]
            self.samplingInterval = pd.to_timedelta(parseFrequency(self.asciiHeader[1][1])).total_seconds()
            self.samplingFrequency = (1.0 / self.samplingInterval)
            self.frameSize = int(self.asciiHeader[1][2])
            self.tableSize = int(self.asciiHeader[1][3])
            self.validationStamp = int(self.asciiHeader[1][4])
            self.compValidationStamp=(0xFFFF^self.validationStamp)
            self.frameResolution = pd.to_timedelta(parseFrequency(self.asciiHeader[1][5])).total_seconds()
            # Extract metadata for each variable.  Add the metadata for timestamp and record which are parsed from the data frames and not in the header
            self.implicitColumns = self.timestampName+[self.recordName]
            self.traceMetadata = {
                columnName:csiTrace(originalVariable=columnName,units = units, operation = operation,dtype=dtype,traceMetadata=self.traceMetadata).to_dict(keepNull=False)
                    for columnName,units,operation,dtype in 
                    zip(
                        self.implicitColumns+self.asciiHeader[2],
                        ['s','ns','']+self.asciiHeader[3],
                        [None,None,None]+self.asciiHeader[4],
                        ['<i4','<i4','<u4']+self.asciiHeader[5]
                        )
                    }
            if self.extractData:
                self.readFrames()
                self.finishTable()
        # for key,value in self.traceMetadata.items():
        #     self.traceMetadata[key] = dcToDict(value,repr=True)
            
    
    def readFrames(self):
        # Parameters dictating extraction
        self.byteMap = ''.join([var['byteMap'] for key,var in self.traceMetadata.items() if key not in self.implicitColumns])     
        self.recordSize = struct.calcsize('>'+self.byteMap)
        self.recordsPerFrame = int((self.frameSize-self.headerSize-self.footerSize)/self.recordSize)
        nframes = int((self.fileSize-self.fileObject.tell())/self.frameSize)
        self.byteMap_Body = '>'+''.join([self.byteMap for r in range(self.recordsPerFrame)])
        # Extract the binary data
        bindata = self.fileObject.read()
        # Process frame by frame
        frames = [f for i in range(nframes) for f in 
                self.decodeFrame(bindata[i*self.frameSize:(i+1)*self.frameSize])]
        self.dataTable = pd.DataFrame(frames,
            columns=self.implicitColumns+[col for col in self.traceMetadata if col not in self.implicitColumns])
        self.typeMap = {key:var['dtype'] for key,var in self.traceMetadata.items()}
        self.dataTable = self.dataTable.astype(self.typeMap)  

    def decodeFrame(self,frame):
        frame = [struct.unpack('iii', frame[:self.headerSize]),
                 struct.unpack(self.byteMap_Body, frame[self.headerSize:-self.footerSize]),
                 struct.unpack('i',frame[-self.footerSize:])[0]]
        # frame[0] = [frame[0][0]+frame[0][1]*self.frameResolution+self.campbellBaseTime,frame[0][2]]
        # Use nanoseconds so timestamp can be stored as int64 instead of float64, avoids floating point precision issues
        # frame[0] = [int((frame[0][0]+self.campbellBaseTime)*1e9)+int((frame[0][1]*self.frameResolution)*1e9),frame[0][2]]
        frame[0] = [int((frame[0][0]+self.campbellBaseTime)),int((frame[0][1]*self.frameResolution)*1e9),frame[0][2]]
        if 'H' in self.byteMap_Body:
            frame[1] = self.decode_fp2(frame[1])
        frame[1] = list(frame[1])
        npr = int(len(frame[1])/self.recordsPerFrame)
        frame[1] = [frame[1][i*npr:(i+1)*npr] for i in range(self.recordsPerFrame)]
        # True/False flag for valid frame
        # Adapted from https://github.com/ansell/camp2ascii/blob/cea750fb721df3d3ccc69fe7780b372d20a8160d/frame_read.c#L109
        footerValidation = (0xFFFF0000 & frame[2]) >> 16
        footerOffset = (0x000007FF & frame[2])
        frame[2] = (footerValidation == self.validationStamp)
        # For handling partial frames
        if frame[2] and footerOffset > 0:
            d = self.frameSize-(footerOffset+self.headerSize+self.footerSize)
            if d:
                offset = int(d/self.recordSize)
            else:
                offset = 0
        else:
            offset = self.recordsPerFrame
        frame = [[int((frame[0][0]+frame[0][1]*1e-9+self.samplingInterval*i)//1),int((frame[0][1]+self.samplingInterval*i*1e9) % 1e9),frame[0][2]+i]+frame[1][i] for i in range(self.recordsPerFrame) if i < offset and frame[2]]
        return(frame)
  
    def decode_fp2(self,Body):
        # adapted from: https://github.com/ansell/camp2ascii/tree/cea750fb721df3d3ccc69fe7780b372d20a8160d
        def FP2_map(int):
            sign = (0x8000 & int) >> 15
            exponent =  (0x6000 & int) >> 13 
            mantissa = (0x1FFF & int)       
            if exponent == 0: 
                Fresult=mantissa
            elif exponent == 1:
                Fresult=mantissa*1e-1
            elif exponent == 2:
                Fresult=mantissa*1e-2
            else:
                Fresult=mantissa*1e-3

            if sign != 0:
                Fresult*=-1
            return Fresult
        FP2_ix = [m.start() for m in re.finditer('H', self.byteMap_Body.replace('>','').replace('<',''))]
        Body = list(Body)
        for ix in FP2_ix:
            Body[ix] = FP2_map(Body[ix])
        return(Body)



    # def resample(self):
        # fileTime = np.ceil(self.dataTable[self.timestampName]/self.databaseInterval)
        # if self.samplingInterval<self.databaseInterval:
        #     for ft in fileTime.unique():
        #         dfColumns = {k:dcToDict(v) for k,v in self.traceMetadata.items() if v.dtype == '<f4'}
        #         df = self.dataTable.loc[fileTime[fileTime==ft].index,list(dfColumns.keys())]
        #         # Output as 1d binary array for processing in eddypro 
        #         # self.ecf32(ft*self.databaseInterval,df,dfColumns,self.databaseInterval)
        #         sys.exit("High frequency data resampling not yet implemented for binary output")
        # else:
        #     sys.exit("Low frequency data resampling not yet implemented for binary output")

        # self.dataTable = self.dataTable.set_index(pd.to_datetime(self.dataTable.TIMESTAMP,unit='s'))
        # if self.samplingInterval<self.databaseInterval:
        #     c = self.dataTable[self.recordName].resample(f'{self.databaseInterval}s').count()
        #     self.dataTable = self.dataTable.resample(f'{self.databaseInterval}s').mean()
        #     self.dataTable[self.recordName] = c.astype('int32')
        #     self.traceMetadata[self.recordName]['dtypeOut'] = '<i4'
        # elif self.samplingInterval>self.databaseInterval:
        #     self.dataTable = self.dataTable.resample(f'{self.databaseInterval}s').nearest()
        # else:
        #     self.dataTable = self.dataTable.resample(f'{self.databaseInterval}s').asfreq()
            
@dataclass(kw_only=True)
class mixedArray(csiTable):
    templateFile: str = None
    nLinesAsciiHeader: int = 0

    def __post_init__(self):
        super().__post_init__()

    def processFile(self):
        if self.templateFile is None and self.extractData is False:
            self.templateFile = self.fileName
            self.readDEF()
        elif self.templateFile is not None:
            self.readDEF()
        elif self.traceMetadata is None:
            self.logError('Missing metadata')
        if self.traceMetadata is not None and self.extractData:
            self.readArray()
            self.finishTable()

    def readDEF(self):
        if self.traceMetadata is None:
            self.traceMetadata = {}
        with open(self.templateFile,'r',encoding='utf-8-sig') as f:
            lines = f.readlines()
        Header,header = '',True
        Wiring,wiring = '',False
        Labels,labels = {},False
        entries = False
        tableID,samplingInterval,Tables,tables,ntables = None,None,{},False,0
        self.mxCols = 0
        for i,l in enumerate(lines):
            if 'final storage' in l:
                Storage = l
            elif 'Output_Table' in l or tables:
                tables = True
                if 'Output_Table' in l:
                    ntables += 1
                    tableID,samplingInterval = [m.strip() for m in l.split('Output_Table')]
                    tableID = int(tableID)
                    Tables[tableID] = ''
                else:
                    Tables[tableID]  = Tables[tableID]+l
            elif 'Table Entries' in l:
                entries = True
            elif 'Labels' in l or labels:
                labels = True
                if 'Labels' not in l:
                    l = l.split()
                    if len(l):
                        if not l[0].isdigit():
                            sensor = '_'.join(l)
                        else:
                            Labels[l[1]]=sensor
            elif 'Wiring' in l or wiring:
                if 'Wiring' in l:
                    self.loggerModel = l.split('for ')[-1].rstrip('-\n')
                wiring = True
                Wiring = Wiring+l
            elif header:
                Header = Header+l

        for ID in Tables:
            data = {'fileName':[],'originalVariable':[],'operation':[],'units':[],'ignore':[]}
            ix = 0
            for v in Tables[ID].split():
                if ix == 1:
                    if v == str(ID):
                        data['fileName'].append(f'{ID}-ID_{v}')
                        ignore=True
                    else:
                        data['fileName'].append(f'{ID}-{v}')
                        if 'RTM' in v:
                            ignore=True
                        else:
                            ignore=False
                    data['originalVariable'].append(v)
                    operation = v.split('_')[-1]
                    if operation not in ['AVG','STD','MAX','MIN','TOT']:
                        operation = ''
                    r = v.rstrip(f'_{operation}').split('_')
                    if r[-1][0].isdigit():
                        r.pop(-1)
                    if len(r)>1:
                        unit = r[-1]
                    else:
                        unit = ''
                    data['operation'].append(operation)
                    data['units'].append(unit)
                    data['ignore'].append(ignore)
                ix += 1
                if ix ==3: ix = 0
            
            df = pd.DataFrame(data=data)
            if len(df.index)>self.mxCols:
                self.mxCols = len(df.index)
            df['sensorID'] = ''
            for l,sensor in Labels.items():
                df.loc[df['originalVariable'].str.contains(l),'sensorID']=sensor
            df.index = df['fileName']
            df = {key:csiTrace.from_dict(value).to_dict() for key,value in df.to_dict('index').items()}
            self.traceMetadata = updateDict(self.traceMetadata,df)
            
    def readArray(self):
        # Count by arrayID prefixes to get max cols
        self.mxCols = pd.DataFrame(data=[k.split('-') for k in self.traceMetadata.keys()],columns=['Array','Cols']).groupby('Array').count().max().values[0]
        df = pd.read_csv(self.fileName,header=None,names=[i for i in range(self.mxCols)])
        cols = list(self.traceMetadata.keys())
        for i,ID in enumerate(df[0].unique()):
            sub = df.loc[df[0]==ID].copy()
            sub = sub.dropna(how='all',axis=1)
            sub.columns = [c for c in cols if int(c.split('-')[0])==ID]
            HHMM = sub[f'{ID}-Hour_Minute_RTM'].astype(str).str.zfill(4)
            HH = HHMM.str[:2]
            MM = HHMM.str[2:4]
            SS = '00'
            HHMM = HH+':'+MM+':'+SS
            YJ = sub[f'{ID}-Year_RTM'].astype(str)+'-'+sub[f'{ID}-Day_RTM'].astype(str)
            sub.index = pd.DatetimeIndex(pd.to_datetime(YJ,format='%Y-%j')+pd.to_timedelta(HHMM))
            if i == 0:
                self.dataTable = sub.copy()
            else:
                self.dataTable = self.dataTable.join(sub,how='outer')
                
