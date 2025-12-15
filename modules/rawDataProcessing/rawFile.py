from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
import modules.rawDataProcessing.parseCSI as parseCSI



@dataclass(kw_only=True)
class sourceFile(baseClass):
    fileFormat: str = field(default=None,metadata={'options':['TOB3','TOA5']})
    fileName: str = None
    traceMetadataMap: dict = field(default_factory=dict,repr=False)

    def __post_init__(self):
        super().__post_init__()

    def parseMetadata(self):
        if hasattr(parseCSI,self.fileFormat):
            csiFile = getattr(parseCSI,self.fileFormat)
            sourceAttributes = csiFile(fileName=self.fileName,extractData=False,traceMetadataMap=self.traceMetadataMap,configFileRoot=self.configFileRoot,configFileName=self.configFileName)
        else:
            self.logError(f"{self.fileFormat} not yet supported")
        return(sourceAttributes)


    def parseFile(self):
        if hasattr(parseCSI,self.fileFormat):
            csiFile = getattr(parseCSI,self.fileFormat)
            csiFile = csiFile(fileName=self.fileName)
        else:
            self.logError(f"{self.fileFormat} not yet supported")

@dataclass(kw_only=True)
class sourceInventory(baseClass):
    sourceDirectory: str
    wildcard: str = None

    def __post_init__(self):
        super().__post_init__()
