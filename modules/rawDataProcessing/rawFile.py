from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
import modules.rawDataProcessing.parseCSI as parseCSI

@dataclass(kw_only=True)
class sourceFile(baseClass):
    # configFileName: str = 'sourceFileConfiguration.yml'
    fileFormat: str = field(default=None,metadata={'options':['TOB3','TOA5']})
    fileName: str = None
    variableSensorMap: dict = field(default_factory=dict,repr=False)

    def __post_init__(self):
        # if self.fileName is not None and self.fileFormat is  None:
        super().__post_init__()
        # breakpoint()

    def parseMetadata(self):
        if hasattr(parseCSI,self.fileFormat):
            csiFile = getattr(parseCSI,self.fileFormat)
            sourceAttributes = csiFile(fileName=self.fileName,extractData=False,variableSensorMap=self.variableSensorMap,configFileRoot=self.configFileRoot,configFileName=self.configFileName)
            # if self.variableSensorMap != {}:
            #     for key,var in sourceAttributes.dataColumns.items():
            #         if var['variableName'] in 
            #         breakpoint()
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
