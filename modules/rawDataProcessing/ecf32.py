from modules.helperFunctions.baseClass import baseClass
# from modules.rawDataProcessing.rawFile import sourceFile
from modules.databaseSetup.configurations import dataSourceConfiguration
from dataclasses import dataclass, field
import numpy as np
import time
import yaml
import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'metadata_eddypro_map.yml')) as f:
    metadataMap = yaml.safe_load(f)


@dataclass(kw_only=True)
class ecf32(dataSourceConfiguration):
    template: dict = field(default_factory=lambda:metadataMap)
    metadataFile: dict = None
    # sourceFile
    def __post_init__(self):
        T1 = time.time()
        super().__post_init__()
        print(time.time()-T1)

        # Use eval statements to fill variables
        # Bellow is intenteded for "simple" setup with one sonic & corresponding IRGAS
        # Eddy-pro "supports" defining sonics, but all flux calculations are done based one reference sonic, so secondary sonics give littel extra info
        # Extension to multi-sonic setups could be made but would require minor edits here, and major eddits to EddyPro source code
        i = 0
        integratedSonics = ['IRGASON']
        for n,sensor in enumerate(self.systemConfiguration.sensorConfigurations.values()):
            if 'soinc' in sensor['sensorType']:
                if sensor['sensorModel'] in integratedSonics:
                    i += 1
                for key,value in self.template['METADATA']['Instruments'].items():
                    if key.startswith('instr_s') and value is not None and type(value) is str and value.startswith('sensor['):
                        self.template['METADATA']['Instruments'][key] = eval(value)
                    # elif key.starswith('instr_n') and value is not None and type(value) is str and value.startswith('sensor['):
                # Note this includes integrated sonics, which have sensor type "sonic-...."
                # if sensor['sensorType'] != 'sonic':
                #     for key,value in s

            n = n+i
            print(n)
            # breakpoint()
        for sec in self.template['METADATA'].keys():
            for key,value in self.template['METADATA'][sec].items():
                if value is not None and type(value) is str and value.startswith('self.'):
                    try:
                        self.template['METADATA'][sec][key] = eval(value)
                    except:
                        print(value)
                        breakpoint()
        print(self.template['METADATA']['Project'])
        breakpoint()

    def writeMetadata(self,fileName):
        header = ';GHG_METADATA'