# Writes high-frequency data file in the custom "EPF32" format.
from src._depreciated.measurement_old import eddyCovarianceMeasurement
from src.databaseObjects.project import project
from src.readData.parseCSI import TOA5,TOB3
from modules.helperFunctions.log import log
from modules.helperFunctions.dictFuncs import loadDict

from dataclasses import dataclass, field
from ruamel.yaml import YAML
import numpy as np
import sys
import os

yaml = YAML()


@dataclass(kw_only=True)
class epf32(eddyCovarianceMeasurement):
    sourceFileName: str
    sourceFileType: str = field(metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['TOB3','TOA5','GHG']})
    # measurementType: str = 'highfrequency'
    metadataEddyProMap: dict = field(default_factory=lambda:
                                    loadDict(os.path.join(os.path.dirname(os.path.abspath(__file__)),'config','metadata_eddypro_map.yml'))
                                    )
    f32Array: np.ndarray = field(default_factory=lambda: np.empty(shape=0, dtype=np.float32))
    f32Variables: dict = field(default_factory=dict)

    def __post_init__(self):
        # Read the file first, some metadata should be extracted
        if self.sourceFileType == 'TOA5':
            sourceData = TOA5(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'TOB3':
            sourceData = TOB3(sourceFileName=self.sourceFileName,sourceFileType=self.sourceFileType)
        elif self.sourceFileType == 'GHG':
            log('GHG file type not implemented yet',kill=True)

        self.syncAttributes(sourceData,inheritance=True,overwrite=True)
        self.binaryFormat()
        super().__post_init__()
        # breakpoint()
        self.getMetadata()

    def binaryFormat(self):
        # Ensure all data are in float 32 format
        # Coerce where possible and drop where not
        
        excludeNames = [self.timestampName,self.recordName]
        keepNames = []
        self.logMessage(f'Dropping columns: {" ".join(excludeNames)}')
        for n,var in self.dataColumns.items():
            if var['dtype'] != '<f4' and var['variableName'] not in excludeNames:
                self.logError(f'Develop coercion process, see {var["variableName"]} of type {var["dtype"]}')
                excludeNames.append(var['variableName'])
            elif var['variableName'] not in excludeNames:
                keepNames.append(var['variableName'])
                self.f32Variables[len(keepNames)] = var

        # drop timestamp and record counter (if they are present)
        # Convert dataTable to flattened array in Fortran order
        self.f32Array = self.dataTable[keepNames].values.T.flatten().astype('float32')
        

    def getMetadata(self):
        METADATA = self.metadataEddyProMap['METADATA']
        # First handle the dynamically numbered metadata
        # Instrument Definitions
        Instrument = {} 
        # for key,value in METADATA['Instruments'].items():


        # FileDescription Columns Next
        FileDescription = {}
        for key,value in METADATA['FileDescription'].items():
            if key.startswith('col_n'):
                FileDescription[key] = value
        # for key in FileDescription.keys():
        #     self.metadataEddyProMap['metadata']['FileDescription'].pop(key)
        # for i in range(len(self.f32Variables)):
        #     n = i + 1
        #     for key,value in FileDescription.items():
        #         value = self.query(value,n)
        #         self.metadataEddyProMap['metadata']['FileDescription'][key] = value
        #     # print(self.metadataEddyProMap['metadata']['FileDescription'][key])

        # breakpoint()
        # # IRGA metadata next
        # Instruments = {}
        # for key,value in self.metadataEddyProMap['metadata']['Instruments'].items():
        #     if key.startswith('instr_n+1'):
        #         Instruments[key] = value
        # for key in Instruments.keys():
        #     self.metadataEddyProMap['metadata']['FileDescription'].pop(key)

        # dynamicInst, dynamicCol = {}, {}
        # metadata = self.metadataEddyProMap['metadata']
        # eddypro = {}
        # for label,section in metadata.items():
        #     for key,value in section.items():
        #         print(label,key,value)
        #         if key.startswith('instr_n+1'):
        #             dynamicInst[key] = value
        #         elif key.startswith('col_n'):
        #             dynamicCol[key] = value
        #         else:
        #             value = self.query(value)
        self.logError()
    
    def query(self,value,n=None):
        if value is None:
            out = None
        elif type(value) is str and value.startswith('self.'):
            out = eval(value)
            if out is not None and "['units']" in value:
                translate_to_ep_fmt = {
                    'm/s':'m_sec',
                    'C':'celsius'
                }
                if out in translate_to_ep_fmt:
                    out = translate_to_ep_fmt[out]
                else:
                    out = out.replace('/','_')
        return(out)

