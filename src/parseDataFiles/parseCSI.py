# Reads campbell scientific .dat files in TOA5, TOB3, and mixed array formats

from dataclasses import dataclass,field
from collections import defaultdict

@dataclass(kw_only=True)
class csiTrace:
    defaultTypes = defaultdict(lambda: '<f4',RECORD ='<i8',TIMESTAMP = 'string') # Does not apply to TOB3 which have type specified in header
    csiTypeMap = {
        'FP2':{'struct':'H','output':'<f4'},
        'IEEE4B':{'struct':'f','output':'<f4'},
        'IEEE8B':{'struct':'d','output':'<f8'},
        'LONG':{'struct':'l','output':'<i8'},
        'INT4':{'struct':'i','output':'<i4'},
        'ASCII':{'struct':'s','output':'string'},
    }

    variableName: str
    units: str = None
    dtype: str = None
    operation: str = None
    byteMap: str = field(default=None,repr=False)

    def __post_init__(self):
        
        if self.dtype is None:
            self.dtype = self.defaultTypes[self.variableName]
        elif self.dtype in self.csiTypeMap:
            self.byteMap = self.csiTypeMap[self.dtype]['struct']
            self.dtype = self.csiTypeMap[self.dtype]['output']
        elif self.dtype.startswith('ASCII'):
            self.byteMap = self.dtype.strip('ASCII()') + self.csiTypeMap['ASCII']['struct']
            self.dtype = self.csiTypeMap['ASCII']['output']
        if self.variableName == 'TIMESTAMP':
            self.units = 'PosixTime'
            self.dtypeOut = '<f8'
        if type(self.dtype) != str:
            self.dtype = self.dtype.str
            