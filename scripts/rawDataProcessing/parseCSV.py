from submodules.helperFunctions.safeFormat import safeFormat,cleanString
from submodules.helperFunctions.baseClass import baseClass
import scripts.database.dataLoggers as dataLoggers
from scripts.database.dbTrace import rawTrace
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable
import pandas as pd
import numpy as np
import warnings
import string
import struct
import sys
import re
import os

@dataclass(kw_only=True)
class csvFile(baseClass):
    fileName: str = field(
        metadata={
            'descriptions': 'Name of the raw data file'
            })
    delimiter: str = field(default=',',repr=False)
    encoding: str = field(
        default=None,
        metadata={
            'descriptions': 'Encoding, for reader, if needed'
            }
    )
    skipRows: int = field(
        default = 0,
        metadata={
            'description':'n rows to skip before header'
            }
    )
    headerRows: int = field(
        default = 1,
        metadata={
            'description':'n rows of header values before data following missing data.  Give count of header rows, will translate to pandas format (list og row numbers minus skip row)'
            }
    )
    preamble: str = field(
        default=None,
        init=False,
        metadata={
            'description':'Text in skipped rows'
            }
    )
    timestampFormat: dict = field(
        default_factory=dict,
        metadata={
            'description':'strptime format of datetime columns in key(column) value(strptime) format'
            }
        )
    extractData: bool = field(
        default=True,
        repr=False,
        metadata={
            'description':'True (all data) / False (preview header where applicable)'
            })
    traceMetadata: dict = field(
        default=None,
        repr=False,
        )
    fileFormat: str = field(
        default='csv',
        init=False,
        metadata={
            'description': 'Indicates the type of file (see options)',
            'options':['csv','HOBOcsv']
            })
    dropCols: list = field(
        default_factory=list,
        metadata={'description':'Optional list of columns to drop'})
    dataTable: pd.DataFrame = field(repr=False,init=False)
    datetimeTrace: pd.DataFrame = field(repr=False,init=False)
    dataLogger: dict = field(default_factory=dict,repr=False,init=False)
    
    def __post_init__(self):
        
        super().__post_init__()
        if self.encoding:
            rawFile = open(self.fileName,'r',encoding=self.encoding)
        else:
            rawFile = open(self.fileName,'r')
            
        self.preamble = []
        for i in range(self.skiprows):
            self.preamble.append(''.join(rawFile.readline().rstrip('\n').split(self.delimiter)))
        self.preamble = '\n'.join(self.preamble)
        if hasattr(self,'parsePreamble'):
            self.parsePreamble()

        if self.headerRows >1:
            self.dataTable = pd.read_csv(rawFile,delimiter=self.delimiter,header=[i for i in range(self.headerRows)])
            self.dataTable.columns = ['_'.join(x) for x in self.dataTable.columns]
        else:
            self.dataTable = pd.read_csv(rawFile,delimiter=self.delimiter)

        self.getDateTime()
        if len(self.dropCols)>0:
            self.dropCols = self.dataTable.columns[self.dataTable.columns.str.contains('|'.join(self.dropCols))].values
        self.dataTable = self.dataTable.drop(columns=self.dropCols)
        self.dataTable = self.dataTable.dropna(how='all')

    def getDateTime(self):
        self.datetimeTrace = pd.DataFrame()
        if hasattr(self,'parseDate') and self.parseDate:
            with warnings.catch_warnings():
                warnings.simplefilter("error", category=UserWarning)
                try:
                    TIMESTAMP = pd.to_datetime(self.dataTable[self.timestampName])
                except:
                    self.logWarning('Bulk parsing of timestamp failed, indicating suspicious format.  Parsed individually assuming yearfirst=True. Double check results.  For better performance, explicitly provide timestamp format.')
                    TIMESTAMP = pd.to_datetime(self.dataTable[self.timestampName],format='mixed',yearfirst=True)
        else:
            tmp = pd.Series(['']*self.dataTable.shape[0])
            fmt = ''
            keys = list(self.timestampFormat.keys())
            for k in keys:
                tmp = tmp+' '+self.dataTable[k]
                fmt = fmt+' '+self.timestampFormat[k]  
            TIMESTAMP = pd.to_datetime(tmp,format=fmt)         

        self.dataTable.index = TIMESTAMP
        self.datetimeTrace['datetime'] = TIMESTAMP
        

@dataclass(kw_only=True)
class genericCSV(csvFile):

    def __post_init__(self):
        
        super().__post_init__()

        self.traceMetadata = {
            columnName:rawTrace(originalVariable=columnName,traceMetadata=self.traceMetadata)
            for columnName in self.dataTable.columns
        }
            

@dataclass(kw_only=True)
class HOBOcsv(csvFile):
    parseDate: bool = field(default=True,repr=False)
    timestampName: str = field(default=None)
    skiprows: int = 1
    fileFormat: str = 'HOBOcsv'
    stationName: str = None
    serialNumber: str = None
    dropCols: list = field(default_factory=lambda:['#','Host Connected', 'Stopped', 'End Of File','Readout'],repr=False)

    def __post_init__(self):
        if self.timestampFormat != {} and 'timestampFormat' not in self.traceMetadata:
            self.parseDate = False
        elif 'timestampFormat' in self.traceMetadata:
            self.timestampFormat = self.traceMetadata.pop('timestampFormat')
        elif self.timestampName is None:
            for key,value in self.traceMetadata.items():
                if 'measurementType' in value and value['measurementType'] == 'TIMESTAMP':
                    if 'originalVariable' in value:
                        self.timestampName = value['originalVariable']
                    else:
                        self.timestampName = key
            if self.timestampName is None:
                self.logError('Must specify timestampName name if parseDate = True, or provide timestampFormat explicitly')
        super().__post_init__()        


        if self.traceMetadata != {}:
            partial = True
        else:
            partial = False
        
        tempTraces = {}
        for col in self.dataTable.columns:
            trace = rawTrace(originalVariable=col,partialMatch=partial,traceMetadata=self.traceMetadata)
            tempTraces[trace.fileName] = trace.to_dict(keepNull=False)
        self.traceMetadata = tempTraces
        self.dataTable.columns = [v['fileName'] for v in self.traceMetadata.values()]
    
    def parsePreamble(self):
        logger = getattr(dataLoggers,'HOBO')
        self.preamble = self.preamble.split('Plot Title: ')[-1]
        self.serialNumber,self.stationName = self.preamble.split('-')
        self.dataLogger = logger(
            stationName=self.stationName,
            serialNumber=self.serialNumber,
            ).to_dict(keepNull=False)