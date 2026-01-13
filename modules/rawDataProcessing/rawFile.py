import os
import yaml
from typing import Iterable
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.dictFuncs import loadDict
import modules.rawDataProcessing.parseCSI as parseCSI


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','traceMetadataMap.yml')) as f:
    traceMap = yaml.safe_load(f)

@dataclass(kw_only=True)
class sourceFile(baseClass):
    fileName: str = None
    fileFormat: str = field(default=None,metadata={'options':['TOB3','TOA5']})
    sourceType: str = field(default=None,metadata={'options':['CSI','LICOR']},repr=False)
    traceMetadataMap: Iterable = field(default=None,repr=False)
    kwargs: Iterable = field(default=None,repr=False)

    def __post_init__(self):
        super().__post_init__()

    def parseMetadata(self):
        if self.fileName is None:
            sourceAttributes = baseClass()
        else:
            if self.fileFormat is None:
                self.getFormat()
            if type(self.traceMetadataMap) is str and self.traceMetadataMap in traceMap.keys():
                self.traceMetadataMap = traceMap[self.traceMetadataMap]
            if hasattr(parseCSI,self.fileFormat):
                csiFile = getattr(parseCSI,self.fileFormat)
                sourceAttributes = csiFile(fileName=self.fileName,extractData=False,traceMetadataMap=self.traceMetadataMap,rootPath=self.rootPath,configName=self.configName)
            else:
                self.logError(f"{self.fileFormat} not yet supported")
        return(sourceAttributes.to_dict())


    def parseFile(self):
        if hasattr(parseCSI,self.fileFormat):
            csiFile = getattr(parseCSI,self.fileFormat)
            csiFile = csiFile.from_dict(self.kwargs|{'fileName':self.fileName})
            data = csiFile.dataTable
            timestamp = csiFile.datetimeTrace
        else:
            self.logError(f"{self.fileFormat} not yet supported")
        return(data,timestamp)

    def getFormat(self):
        if self.sourceType == 'CSI':
            self.fileFormat = parseCSI.csiType(self.fileName).fileType
        elif self.sourceType == 'LICOR':
            self.fileFormat = 'GHG'
        else:
            breakpoint()

