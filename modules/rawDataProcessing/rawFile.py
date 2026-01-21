import os
import yaml
from typing import Iterable
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.dictFuncs import loadDict
import modules.rawDataProcessing.parseCSI as parseCSI


# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','traceMetadata.yml')) as f:
#     traceMap = yaml.safe_load(f)

@dataclass(kw_only=True)
class sourceFile(baseClass):
    fileName: str = None
    fileFormat: str = field(default=None,metadata={'options':['TOB3','TOA5']})
    sourceFileType: str = field(default=None,metadata={'options':['CSI','LICOR']},repr=False)
    traceMetadata: Iterable = field(default=None,repr=False)
    kwargs: Iterable = field(default=None,repr=False)

    def __post_init__(self):
        super().__post_init__()

    def parseMetadata(self):
        if self.fileName is None:
            sourceAttributes = baseClass()
        else:
            if self.fileFormat is None:
                self.getFormat()
            self.logWarning('traceMap?',verbose=True)
            # if type(self.traceMetadata) is str and self.traceMetadata in traceMap.keys():
            #     self.traceMetadata = traceMap[self.traceMetadata]
            if hasattr(parseCSI,self.fileFormat):
                csiFile = getattr(parseCSI,self.fileFormat)
                sourceAttributes = csiFile(fileName=self.fileName,extractData=False,traceMetadata=self.traceMetadata,rootPath=self.rootPath,configName=self.configName,verbose=self.verbose)
            else:
                self.logError(f"{self.fileFormat} not yet supported")
        return(sourceAttributes.to_dict())


    def parseFile(self):
        if hasattr(parseCSI,self.fileFormat):
            csiFile = getattr(parseCSI,self.fileFormat)
            csiFile = csiFile.from_dict(self.kwargs|{'fileName':self.fileName,'verbose':self.verbose})
            data = csiFile.dataTable
            timestamp = csiFile.datetimeTrace
            # data.index=timestamp.datetime
        else:
            self.logError(f"{self.fileFormat} not yet supported")
        return(data,timestamp)

    def getFormat(self):
        if self.sourceFileType == 'CSI':
            self.fileFormat = parseCSI.csiType(self.fileName).fileType
        elif self.sourceFileType == 'LICOR':
            self.fileFormat = 'GHG'
        else:
            breakpoint()

