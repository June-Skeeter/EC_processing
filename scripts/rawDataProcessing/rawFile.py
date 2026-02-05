# import os
# import yaml
# from typing import Iterable
from submodules.helperFunctions.baseClass import baseClass
from dataclasses import dataclass, field
import pandas as pd
# from submodules.helperFunctions.dictFuncs import loadDict
# import scripts.rawDataProcessing.parseCSI as parseCSI

@dataclass(kw_only=True)
class sourceFile(baseClass):
    fileName: str = field(
        metadata={
            'descriptions': 'Name of the raw data file'
            })
    
    fileFormat: str = field(
        init=False,
        metadata={
            'description': 'Indicates the type of file (see options)',
            'options':['TOB3','TOA5','HOBOcsv']
            })
    
    dataTable: pd.DataFrame = field(
        repr=False,
        init=False,
        metadata={'description':'dataframe with datetime index and columns of data traces'}
        )
    datetimeTrace: pd.DataFrame = field(
        repr=False,
        init=False,
        metadata={'description':'dataframe index and columns of date'}
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
        metadata={'description':'dict of metadata describing each trace'})


    def __post_init__(self):
        super().__post_init__()
# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','traceMetadata.yml')) as f:
#     traceMap = yaml.safe_load(f)

# @dataclass(kw_only=True)
# class sourceFile(baseClass):
#     fileName: str = None
#     fileFormat: str = field(default=None,metadata={'options':['TOB3','TOA5','GHG']})
#     sourceFileType: str = field(default=None,metadata={'options':['CSI','LICOR']},repr=False)
#     traceMetadata: Iterable = field(default=None,repr=False)
#     kwargs: Iterable = field(default=None,repr=False)

#     def __post_init__(self):
#         super().__post_init__()

#     def parseMetadata(self):
#         if self.fileName is None:
#             sourceAttributes = baseClass()
#         else:
#             if self.fileFormat is None:
#                 self.getFormat()
#             # self.logWarning('traceMap?',verbose=True)
#             # if type(self.traceMetadata) is str and self.traceMetadata in traceMap.keys():
#             #     self.traceMetadata = traceMap[self.traceMetadata]
#             if hasattr(parseCSI,self.fileFormat):
#                 csiFile = getattr(parseCSI,self.fileFormat)
#                 sourceAttributes = csiFile(fileName=self.fileName,extractData=False,traceMetadata=self.traceMetadata,rootPath=self.rootPath,configName=self.configName,verbose=self.verbose)
#             else:
#                 self.logError(f"{self.fileFormat} not yet supported")
#         return(sourceAttributes.to_dict())

#     def parseFile(self):
#         if hasattr(parseCSI,self.fileFormat):
#             csiFile = getattr(parseCSI,self.fileFormat)
#             csiFile = csiFile.from_dict(self.kwargs|{'fileName':self.fileName,'verbose':self.verbose})
#             data = csiFile.dataTable
#             timestamp = csiFile.datetimeTrace
#             # data.index=timestamp.datetime
#         else:
#             self.logError(f"{self.fileFormat} not yet supported")
#         return(data,timestamp)

#     def getFormat(self):
#         if self.sourceFileType == 'CSI':
#             self.fileFormat = parseCSI.csiType(self.fileName).fileType
#         elif self.sourceFileType == 'LICOR':
#             self.fileFormat = 'GHG'
#         else:
#             breakpoint()

