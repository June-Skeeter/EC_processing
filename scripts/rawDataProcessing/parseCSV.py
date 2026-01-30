# try:
#     # relative import for use as submodules
#     from .baseMethods import * 
# except:
#     # absolute import for use as standalone
#     from baseMethods import * 
    

from dataclasses import dataclass, field
from submodules.helperFunctions.baseClass import baseClass
import scripts.database.dataLoggers as dataLoggers
from scripts.database.dbTrace import rawTrace
import pandas as pd
from datetime import datetime
from typing import Iterable
import warnings
import numpy as np
import struct
import sys
import re
import os


@dataclass(kw_only=True)
class genericCSV(baseClass):
    fileName: str = field(
        metadata={
            'descriptions': 'Name of the raw data file'
            })

    skipRows: int = 0
    headerRows: int = 1
    program: str = None
    dataTable: pd.DataFrame = field(repr=False,init=False)
    datetimeTrace: pd.DataFrame = field(repr=False,init=False)
    fileTimestamp: datetime = field(repr=False,init=False)
    dataLogger: dict = field(default_factory=dict,repr=False,init=False)
    timestampName: str = None
    timestampFormat: dict = field(default_factory=dict)
    extractData: bool = field(
        default=True,
        repr=False,
        metadata={
            'description':'True (all data) / False (preview header where applicable)'
            })
    traceMetadata: dict = field(default=None,repr=False)
    fileFormat: str = field(
        default='csv',
        init=False,
        metadata={
            'description': 'Indicates the type of file (see options)',
            'options':['csv','HOBOcsv']
            })
    dropCols: list = field(default_factory=list)

    def __post_init__(self):
        
        super().__post_init__()
        rawFile = open(self.fileName,'r')#,encoding='utf-8-sig')
        T = []
        for i in range(self.skiprows):
            T .append(rawFile.readline().rstrip('\n'))
            
        self.dataTable = pd.read_csv(rawFile)

        if self.timestampFormat == 'auto':
            if self.timestampName is None:
                self.logError('Must specify timestampName to use auto-detection')
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("error", category=UserWarning)
                    try:
                        TIMESTAMP = pd.to_datetime(self.dataTable[self.timestampName])
                    except:
                        self.logWarning('Bulk parsing of timestamp failed, indicating suspicious format.  Parsed individually assuming yearfirst=True. Double check results.  For better performance, explicitly provide timestamp format.')
                        TIMESTAMP = pd.to_datetime(self.dataTable[self.timestampName],format='mixed',yearfirst=True)
                self.dataTable = self.dataTable.drop(columns=self.timestampName)
        else:
            tmp = pd.Series(['']*self.dataTable.shape[0])
            fmt = ''
            keys = list(self.timestampFormat.keys())
            for k in keys:
                tmp = tmp+' '+self.dataTable[k]
                fmt = fmt+' '+self.timestampFormat[k]
            TIMESTAMP = pd.to_datetime(tmp,format=fmt)
            self.dataTable = self.dataTable.drop(columns=keys)

        self.dataTable.index = TIMESTAMP
        if len(self.dropCols)>0:
            self.dropCols = self.dataTable.columns[self.dataTable.columns.str.contains('|'.join(self.dropCols))].values
        self.dataTable = self.dataTable.drop(columns=self.dropCols)
        self.dataTable = self.dataTable.dropna(how='all')

@dataclass(kw_only=True)
class HOBOcsv(genericCSV):
    timestampName: str
    timestampFormat: str = 'auto'
    skiprows: int = 1
    fileFormat: str = 'HOBOcsv'
    dropCols: list = field(default_factory=lambda:['#','Host Connected', 'Stopped', 'End Of File'],repr=False)

    def __post_init__(self):
        super().__post_init__()        
        breakpoint()
        