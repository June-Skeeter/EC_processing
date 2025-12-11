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
        for key,value in self.template['METADATA']['Project'].items():
            if value is not None and type(value) is str and value.startswith('self.'):
                print(eval(value))
        breakpoint()

    def writeMetadata(self,fileName):
        header = ';GHG_METADATA'