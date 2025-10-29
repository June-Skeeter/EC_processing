# Writes high-frequency data file in the custom "EPF32" format.
from ..dbFunctions.siteAttributes import siteAttributes
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
class measurementMetadata(siteAttributes):
    measurementID: str = None
    measurementType: str = None
    samplingFrequency: float = None  # in Hz
    samplingInterval: float = None # in seconds

    def __post_init__(self):
        self.__post_init__()
        if self.samplingInterval is not None:
            self.samplingFrequency = 1.0 / self.samplingInterval

        if self.measurementID is None:
            self.logError("measurementID must be provided")
        configPath = os.path.join(self.projectPath, 'Sites', self.siteID, 'measurementMetadata.yml')

        


@dataclass(kw_only=True)
class ecMetadata(measurementMetadata):
    measurementType: str = 'EC'
    sonicNorthOffset: float = None
    sonicAnemometer: str = field(default=None,metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['IRGASON','CSAT3','CSAT3B']})

    def __post_init__(self):
        super().__post_init__()
        fn = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')    
        with open(fn, 'r') as file:
            self.metadataEddyProMap = yaml.load(file)
        for subset in ['metadata','eddypro']:
            for key,value in self.metadataEddyProMap[subset].items():
                if type(value) is str and value.startswith('self.'):
                    self.metadataEddyProMap[subset][key] = eval(value)
            


@dataclass(kw_only=True)
class epf32(ecMetadata):
    sourceFileName: str
    sourceFileType: str = field(metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['TOB3','TOA5','GHG']})
    measurementType: str = 'highfrequency'
    metadataEddyProMap: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')

    def __post_init__(self):
        # Read the file first, some metadata should be extracted
        if self.sourceFileType == 'TOA5':
            self.source = TOA5(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'TOB3':
            self.source = TOB3(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'GHG':
            log('GHG file type not implemented yet',kill=True)

        log('Consider developing routine for auto-dumpping all metadata from source file')
        for key,value in self.source.__dict__.items():
            if key in self.__dataclass_fields__.keys() and value is not None:
                setattr(self,key,value)
        
        super().__post_init__()
        # binArray = self.source.dataTable.values.T.flatten().astype('float32')
        print(self.samplingFrequency,self.samplingInterval)
        breakpoint()

