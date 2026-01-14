# Reads campbell scientific .dat files in TOA5, TOB3, and mixed array (not yet supported) formats

from dataclasses import dataclass,field
from collections import defaultdict
from modules.helperFunctions.log import log
from modules.helperFunctions.parseFrequency import parseFrequency
from modules.helperFunctions.dictFuncs import dcToDict
from modules.helperFunctions.baseClass import baseClass
import modules.databaseSetup.dataLoggers as dataLoggers
from modules.rawDataProcessing.rawTrace import rawTraceIn
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
class csiTrace(rawTraceIn):
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
            self.dtype = self.defaultTypes[self.variableNameIn]
        elif self.dtype in self.csiTypeMap:
            self.byteMap = self.csiTypeMap[self.dtype]['struct']
            self.dtype = self.csiTypeMap[self.dtype]['output']
        elif type(self.dtype) is str and self.dtype.startswith('ASCII'):
            self.byteMap = self.dtype.strip('ASCII()') + self.csiTypeMap['ASCII']['struct']
            self.dtype = self.csiTypeMap['ASCII']['output']
        if self.variableNameIn == 'TIMESTAMP':
            self.units = 'datetime'
            # self.dtype = '<i8'
        if type(self.dtype) != str:
            self.dtype = self.dtype.str
        super().__post_init__()

@dataclass(kw_only=True)
class csiFile(baseClass):
    # Some files may contain multiple tables
    # Attributes common to a given file
    fileObject: object = field(default=None,repr=False,init=False)
    dataLogger: dict = field(default_factory=dict,repr=False,init=False)
    stationName: str = None
    loggerModel: str = None
    serialNumber: str = None
    program: str = None
    dataTable: pd.DataFrame = field(repr=False,init=False)
    datetimeTrace: pd.DataFrame = field(repr=False,init=False)
    fileTimestamp: datetime = field(repr=False,init=False)
    campbellBaseTime: float = field(
        default=631152000.0,
        repr=False,
        init=False,
        metadata={
            'description':'Start of CSI epoch in POSIX epoch: pd.to_datetime("1990-01-01").timestamp()'
            })
    fileFormat: str = field(
        init=False,
        metadata={
            'description': 'Indicates the type of file (see options)',
            'options':['TOB3','TOA5']
            })
    fileName: str = field(
        metadata={
            'descriptions': 'Name of the raw data file'
            })
    extractData: bool = field(
        default=True,
        repr=False,
        metadata={
            'description':'True (all data) / False (preview header where applicable)'
            })
    traceMetadataMap: dict = field(default=None,repr=False)
    
    def __post_init__(self):
        self.UID = self.program.split(':')[-1].replace('.','-')
        super().__post_init__()
        self.processFile()
        if hasattr(dataLoggers,self.loggerModel):
            logger = getattr(dataLoggers,self.loggerModel)
            self.dataLogger = logger(
                stationName=self.stationName,
                serialNumber=self.serialNumber,
                ).to_dict(keepNull=False)
        
    
@dataclass(kw_only=True)
class csiTable(csiFile):
    # Attributes common to a CSI format datable
    asciiHeader: list = field(init=False,repr=False)
    nLinesAsciiHeader: int = field(repr=False)
    tableName: str = None
    dataColumns: dict = field(default_factory=dict)
    timestampName: str = field(default='TIMESTAMP',init=False,repr=False)
    recordName: str = field(default='RECORD',init=False,repr=False)
    samplingInterval: float = field(default=None,init=None)  # in seconds
    samplingFrequency: str = field(default=None,init=None) # in Hz
    gpsDriftCorrection: bool = field(default=False,repr=False,metadata={'description':'Consider using for high frequency data if GPS clock resets were enabled.  This clock correction is useful to ensure long-term stability of the data logger clock but causes problems when splitting high-frequency data files.  Assuming the file does not span more than a day, the drift should be minimal, so we can "remove" the offset within a file to ensure timestamps are sequential'})
    mode: str = field(default='r',repr=False)

    def __post_init__(self):
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
        if is_datetime(self.dataTable[self.timestampName]):
            self.datetimeTrace['datetime'] = self.dataTable[self.timestampName]
        else:
            self.datetimeTrace['datetime'] = pd.to_datetime((self.dataTable['POSIX_Time']*1e9).astype('int64')+self.dataTable['NANOSECONDS'],unit='ns') 
            # self.dataTable.index = pd.to_datetime((self.dataTable['POSIX_Time']*1e9).astype('int64')+self.dataTable['NANOSECONDS'],unit='ns') 
        # breakpoint()
        if self.gpsDriftCorrection:
            # Identify gaps in time series
            Offset = (self.dataTable[self.timestampName].diff().fillna(self.samplingInterval)-self.samplingInterval).cumsum()
            self.dataTable[self.timestampName] -= Offset
            if self.verbose:
                log(f"Total GPS induced offset in {self.fileName} is {Offset.iloc[-1]}s",verbose=False)
        
@dataclass(kw_only=True)
class TOA5(csiTable):
    nLinesAsciiHeader: int = field(default=4,repr=False,init=False)
    fileFormat: str = 'TOA5'
        
    def processFile(self):
        #First read metadata from files header
        self.fileTimestamp = datetime.strptime(re.search(r'([0-9]{4}\_[0-9]{2}\_[0-9]{2}\_[0-9]{4})', self.fileName.rsplit('.',1)[0]).group(0),'%Y_%m_%d_%H%M')
        # with open(self.fileName) as self.fileObject:
        #     self.readAsciiHeader()
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
        self.dataColumns =  {
            columnName:csiTrace(variableNameIn=columnName,units=units,operation=operation,dtype=dtype,traceMetadataMap=self.traceMetadataMap).to_dict(keepNull=False)
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
            self.dataColumns = {
                columnName:csiTrace(variableNameIn=columnName,units = units, operation = operation,dtype=dtype,traceMetadataMap=self.traceMetadataMap).to_dict(keepNull=False)
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
        # for key,value in self.dataColumns.items():
        #     self.dataColumns[key] = dcToDict(value,repr=True)
            
    
    def readFrames(self):
        # Parameters dictating extraction
        self.byteMap = ''.join([var['byteMap'] for key,var in self.dataColumns.items() if key not in self.implicitColumns])     
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
            columns=self.implicitColumns+[col for col in self.dataColumns if col not in self.implicitColumns])
        self.typeMap = {key:var['dtype'] for key,var in self.dataColumns.items()}
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
                offset = int(self.recordSize/d)
            else:
                offset = 0
        else:
            offset = self.recordsPerFrame
        frame = [[int((frame[0][0]+frame[0][1]*1e-9+self.samplingInterval*i)//1),int((frame[0][1]+self.samplingInterval*i*1e9) % 1e9),frame[0][2]+i]+frame[1][i] for i in range(self.recordsPerFrame) if i < offset and frame[2]]
        
        # frame = [[frame[0][0]+(self.samplingInterval*1e9)*i,frame[0][1]+i]+frame[1][i] for i in range(self.recordsPerFrame) if i < offset and frame[2]]
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
        #         dfColumns = {k:asdict_repr(v) for k,v in self.dataColumns.items() if v.dtype == '<f4'}
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
        #     self.dataColumns[self.recordName]['dtypeOut'] = '<i4'
        # elif self.samplingInterval>self.databaseInterval:
        #     self.dataTable = self.dataTable.resample(f'{self.databaseInterval}s').nearest()
        # else:
        #     self.dataTable = self.dataTable.resample(f'{self.databaseInterval}s').asfreq()
            