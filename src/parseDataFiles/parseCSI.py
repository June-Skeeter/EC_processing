# Reads campbell scientific .dat files in TOA5, TOB3, and mixed array (not yet supported) formats

from dataclasses import dataclass,field
from collections import defaultdict
from ..helperFunctions.log import log
from ..helperFunctions.parseFrequency import parseFrequency
from ..helperFunctions.dictFuncs import dcToDict
from ..dbFunctions.measurement_old import trace
from ..helperFunctions.baseClass import baseClass
import pandas as pd
import os
from datetime import datetime
import numpy as np
import struct
import sys
import re

@dataclass(kw_only=True)
class csiTrace(trace):
    defaultTypes = defaultdict(lambda: '<f4',RECORD ='<i8',TIMESTAMP = 'string') # Does not apply to TOB3 which have type specified in header
    csiTypeMap = {
        'FP2':{'struct':'H','output':'<f4'},
        'IEEE4B':{'struct':'f','output':'<f4'},
        'IEEE8B':{'struct':'d','output':'<f8'},
        'LONG':{'struct':'l','output':'<i8'},
        'INT4':{'struct':'i','output':'<i4'},
        'ASCII':{'struct':'s','output':'string'},
    }
    # Parsed from data file
    operation: str = None
    byteMap: str = field(default=None,repr=False)

    def __post_init__(self):
        if self.dtype is None:
            self.dtype = self.defaultTypes[self.variableName]
        elif self.dtype in self.csiTypeMap:
            self.byteMap = self.csiTypeMap[self.dtype]['struct']
            self.dtype = self.csiTypeMap[self.dtype]['output']
        elif type(self.dtype) is str and self.dtype.startswith('ASCII'):
            self.byteMap = self.dtype.strip('ASCII()') + self.csiTypeMap['ASCII']['struct']
            self.dtype = self.csiTypeMap['ASCII']['output']
        if self.variableName == 'TIMESTAMP':
            self.units = 'PosixTime'
            self.dtypeOut = '<f8'
        if type(self.dtype) != str:
            self.dtype = self.dtype.str

@dataclass(kw_only=True)
class csiFile(baseClass):
    # Some files may contain multiple tables
    # Attributes common to a given file
    fileObject: object = field(default=None,repr=False)
    StationName: str = None
    LoggerModel: str = None
    SerialNo: str = None
    program: str = None
    dataTable: pd.DataFrame = None
    fileTimestamp: datetime = None
    campbellBaseTime: float = field(default=631152000.0,repr=False,metadata={'description':'Start of CSI epoch in POSIX epoch: pd.to_datetime("1990-01-01").timestamp()'})
    sourceFileName: str = field(metadata={'descriptions': 'Name of the raw data file'})
    sourceFileType: str = field(metadata={
        'description': 'Indicates the type of file (see options)',
        'options':['TOB3','TOA5']})
    
    
@dataclass(kw_only=True)
class csiTable(csiFile):
    # Attributes common to a CSI format datable
    tableName: str = None
    dataColumns: str = None
    extractData: bool = field(default=True,repr=False)
    timestampName: str = 'TIMESTAMP'
    recordName: str = 'RECORD'
    samplingInterval: float = None  # in seconds
    samplingFrequency: str = None # in Hz
    gpsDriftCorrection: bool = field(default=False,repr=False,metadata={'description':'Consider using for high frequency data if GPS clock resets were enabled.  This is clock correction is useful to ensure long-term stability of the data logger clock but causes problems when splitting high-frequency data files.  Assuming the file does not span more than a day, the drift should be minimal, so we can "remove" the offset within a file to ensure timestamps are sequential'})

    def readAsciiHeader(self,nLines):
        Header = [self.readAsciiLine(self.fileObject.readline()) for l in range(nLines)]
        if self.sourceFileType != Header[0][0]:
            log(f"{self.sourceFileName} is not in {self.sourceFileType} format",traceback=False,kill=True)
        self.StationName=Header[0][1]
        self.LoggerModel=Header[0][2]
        self.SerialNo=Header[0][3]
        return(Header)
    
    def readAsciiLine(self,line):
        if type(line) == str:
            return(line.strip().replace('"','').split(','))
        else:
            return(line.decode('ascii').strip().replace('"','').split(','))
        
    def finishTable(self):
        if self.gpsDriftCorrection:
            # Identify gaps in time series
            Offset = (self.dataTable[self.timestampName].diff().fillna(self.samplingInterval)-self.samplingInterval).cumsum()
            self.dataTable[self.timestampName] -= Offset
            if self.verbose:
                log(f"Total GPS induced offset in {self.sourceFileName} is {Offset.iloc[-1]}s",verbose=False)
        if self.samplingInterval is None:
            self.samplingInterval = self.dataTable.TIMESTAMP.diff().median().total_seconds()
        self.samplingFrequency = (1.0 / self.samplingInterval)
        for key,value in self.dataColumns.items():
            self.dataColumns[key] = dcToDict(value,repr=True)
        
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
            
@dataclass(kw_only=True)
class TOA5(csiTable):

    def __post_init__(self):
        #First read metadata from files header
        self.fileTimestamp = datetime.strptime(re.search(r'([0-9]{4}\_[0-9]{2}\_[0-9]{2}\_[0-9]{4})', self.sourceFileName.rsplit('.',1)[0]).group(0),'%Y_%m_%d_%H%M')
        with open(self.sourceFileName) as self.fileObject:
            Header = self.readAsciiHeader(nLines=4)
            self.tableName = Header[0][-1]
    
        self.dataTable = pd.read_csv(self.sourceFileName,skiprows=[0,2,3],header=[0],parse_dates=[self.timestampName],date_format='ISO8601',dtype=csiTrace.defaultTypes)
        
        # Extract metadata for each variable
        self.dataColumns =  {
            columnName:csiTrace(variableName=columnName,units=units,operation=operation,dtype=dtype)#.__dict__
                for columnName,units,operation,dtype in 
                zip(Header[1],Header[2],Header[3],list(self.dataTable.dtypes))}
        self.finishTable()


@dataclass(kw_only=True)
class TOB3(csiTable):
    headerSize = 12
    footerSize = 4
    byteMap: str = None

    def __post_init__(self):
        #First read metadata from files header
        self.fileSize = os.path.getsize(self.sourceFileName)
        with open(self.sourceFileName,'rb') as self.fileObject:
            Header = self.readAsciiHeader(nLines=6)
            self.fileTimestamp = pd.to_datetime(Header[0][-1])
            self.tableName = Header[1][0]
            self.samplingInterval = pd.to_timedelta(parseFrequency(Header[1][1])).total_seconds()
            self.frameSize = int(Header[1][2])
            self.tableSize = int(Header[1][3])
            self.validationStamp = int(Header[1][4])
            self.compValidationStamp=(0xFFFF^self.validationStamp)
            self.frameResolution = pd.to_timedelta(parseFrequency(Header[1][5])).total_seconds()
            # Extract metadata for each variable
            self.dataColumns = {
                columnName:csiTrace(variableName=columnName,units = units, operation = operation,dtype=dtype)
                    for i,(columnName,units,operation,dtype) in 
                    enumerate(zip(Header[2],Header[3],Header[4],Header[5]))
                    }
            if self.extractData:
                self.readFrames()
                self.finishTable()
    
    def readFrames(self):
        # Parameters dictating extraction
        self.byteMap = ''.join([var.byteMap for var in self.dataColumns.values()])     
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
            columns=[self.timestampName,self.recordName]+[col for col in self.dataColumns])
        self.dataColumns = {
            columnName:csiTrace(variableName=columnName,units = units, operation = operation,dtype=dtype)
                    for columnName,units,operation,dtype in 
                    zip([self.timestampName,self.recordName],['s',None],[None,None],['<f8','<i8'])
                    } | self.dataColumns
        self.typeMap = {key:val.dtype for key,val in self.dataColumns.items()}
        self.dataTable = self.dataTable.astype(self.typeMap)  

    def decodeFrame(self,frame):
        frame = [struct.unpack('iii', frame[:self.headerSize]),
                 struct.unpack(self.byteMap_Body, frame[self.headerSize:-self.footerSize]),
                 struct.unpack('i',frame[-self.footerSize:])[0]]
        frame[0] = [frame[0][0]+frame[0][1]*self.frameResolution+self.campbellBaseTime,frame[0][2]]
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
        frame = [[frame[0][0]+self.samplingInterval*i,frame[0][1]+i]+frame[1][i] for i in range(self.recordsPerFrame) if i < offset and frame[2]]
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
