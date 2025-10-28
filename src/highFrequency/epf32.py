# Writes high-frequency data file in the custom "EPF32" format.
from ..siteMetadata.siteAttributes import siteAttributes
from ..helperFunctions.typeEnforcer import typeEnforcer
from ..parseDataFiles.parseCSI import TOA5,TOB3
from ..helperFunctions.log import log

from dataclasses import dataclass, field
import sys
import os
from ruamel.yaml import YAML

yaml = YAML()

# @dataclass(kw_only=True)
# class metadataEddyPro:
#     template: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')

#     def __post_init__(self):
#         with open(self.template, 'r') as file:
#             self.metadata = yaml.load(file)
@dataclass(kw_only=True)
class userMetadata(siteAttributes):
    sonicNorthOffset: float = 0.0
    sonicAnemometer: str = field(default=None,metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['IRGASON','CSAT3','CSAT3B']})

    def __post_init__(self):
        # breakpoint()
        super().__post_init__()
    # def __validate__(self):
    #     print('No?')
    #     print('!?')
    #     super().__post_init__()
    #     sys.exit()


@dataclass(kw_only=True)
class epf32(userMetadata):
    sourceFileName: str
    sourceFileType: str = field(metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['TOB3','TOA5','GHG']})
    measurementType: str = 'highfrequency'
    metadataEddyProMap: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')

    def __post_init__(self):
        super().__post_init__()
        # if self.sourceFileType == 'TOA5':
        #     self.source = TOA5(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        # elif self.sourceFileType == 'TOB3':
        #     self.source = TOB3(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)

        # log('Consider developing routine for auto-dumpping all metadata from source file')
        # for key,value in self.source.__dict__.items():
        #     if key in self.__dataclass_fields__.keys() and value is not None:
        #         setattr(self,key,value)
        
        # super().__post_init__()
        # binArray = self.source.dataTable.values.T.flatten().astype('float32')
        # breakpoint()

