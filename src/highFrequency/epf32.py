# Writes high-frequency data file in the custom "EPF32" format.
from ..siteMetadata.siteAttributes import siteAttributes
from ..parseDataFiles.parseCSI import TOA5,TOB3
from ..helperFunctions.log import log
from dataclasses import dataclass, field

@dataclass(kw_only=True)
class epf32(siteAttributes):
    sourceFileName: str
    sourceFileType: str = field(metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['TOB3','TOA5','GHG']})
    measurementType: str = 'highfrequency'

    def __post_init__(self):
        if self.sourceFileType == 'TOA5':
            self.source = TOA5(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'TOB3':
            self.source = TOB3(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)

        log('Consider developing routine for auto-dumpping all metadata from source file')#print(self.source.__dict__.keys())
        for key,value in self.source.__dict__.items():
            if key in self.__dataclass_fields__.keys() and value is not None:
                setattr(self,key,value)
        
        super().__post_init__()
        # breakpoint()


