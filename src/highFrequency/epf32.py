# Writes high-frequency data file in the custom "EPF32" format.
from ..dbFunctions.measurement import eddyCovarianceMeasurement
from ..dbFunctions.project import project
from ..parseDataFiles.parseCSI import TOA5,TOB3
from ..helperFunctions.log import log

from dataclasses import dataclass, field
import sys
import os
from ruamel.yaml import YAML

yaml = YAML()


@dataclass(kw_only=True)
class epf32(eddyCovarianceMeasurement):
    sourceFileName: str
    sourceFileType: str = field(metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['TOB3','TOA5','GHG']})
    # measurementType: str = 'highfrequency'
    metadataEddyProMap: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')

    def __post_init__(self):
        # Read the file first, some metadata should be extracted
        if self.sourceFileType == 'TOA5':
            sourceData = TOA5(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'TOB3':
            sourceData = TOB3(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'GHG':
            log('GHG file type not implemented yet',kill=True)

        self.snycAttributes(sourceData,inheritance=True,overwrite=True)
        super().__post_init__()

        # binArray = self.source.dataTable.values.T.flatten().astype('float32')


# @dataclass(kw_only=True)
# class test(project):
#     test: str = 'test'
#     def __post_init__(self):
#         super().__post_init__()
#         t = measurement(projectPath=self.projectPath,siteID='SCL2',measurementID='10Hz')
#         for key in t.__annotations__.keys():
#             if not hasattr(self,key):
#                 setattr(self,key,t.__dict__[key])
#         breakpoint()

# @dataclass(kw_only=True)
# class metadataEddyPro:
#     template: str = os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml')

#     def __post_init__(self):
#         with open(self.template, 'r') as file:
#             self.metadata = yaml.load(file)

# @dataclass(kw_only=True)
# class measurementAttributes(siteConfiguration):
#     measurementID: str = None
#     measurementType: str = None
#     samplingFrequency: float = None  # in Hz
#     samplingInterval: float = None # in seconds

#     def __post_init__(self):
#         self.__post_init__()
#         if self.samplingInterval is not None:
#             self.samplingFrequency = 1.0 / self.samplingInterval

#         if self.measurementID is None:
#             self.logError("measurementID must be provided")
#         configPath = os.path.join(self.projectPath, 'Sites', self.siteID, 'measurementAttributes.yml')

