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
    metadataFile: dict = field(default_factory=dict)
    eddyproFile: dict = field(default_factory=dict)
    defaultInterval: int = 30
    integratedSonics: list = field(default_factory=lambda:['IRGASON'])
    # sourceFile
    def __post_init__(self):
        T1 = time.time()
        super().__post_init__()
        print(time.time()-T1)

        # Use eval statements to fill dynamic variables

        # Fill these simple paramters fist
        for sec in ['Project','Files','Site','Station','Timing']:
            self.metadataFile[sec] = {}
            for key,value in self.template['METADATA'][sec].items():
                if value is not None and type(value) is str and value.startswith('self.'):
                    self.metadataFile[sec][key] = eval(value)

        # Next process intruments
        # Bellow is intenteded for "simple" setup with one sonic & corresponding IRGAS
        # Eddy-pro "supports" defining sonics, but all flux calculations are done based one reference sonic, so secondary sonics give littel extra info
        # Extension to multi-sonic setups could be made but would require minor edits here, and major eddits to EddyPro source code
        
        def parsSensor(value,sensor,n):
            if value is None:
                value = ''
            elif type(value) is str and value.startswith('sensor['):
                param = value.split("sensor['")[-1].split("']")[0]
                if param in sensor:
                    value = eval(value)
                    if type(value) is str:
                        value = value.lower()
            return(value)

        i = 1
        self.metadataFile['Instruments'] = {}
        for sensor in self.systemConfiguration.sensorConfigurations.values():
            for key,value in self.template['METADATA']['Instruments'].items():
                self.metadataFile['Instruments'][key.replace('_n_',f"_{i}_")] = parsSensor(value,sensor,i+1)
                if 'sonic' in sensor['sensorType'] and sensor['sensorModel'] in self.integratedSonics:
                    self.metadataFile['Instruments'][key.replace('_n_',f"_{i+1}_")] = parsSensor(value,sensor,i+1)
            if 'sonic' in sensor['sensorType'] and sensor['sensorModel'] in self.integratedSonics:
                i += 2
            else:
                i += 1
        
        self.metadataFile['FileDescription'] = {}
        for variable in self.sourceFileConfiguration.dataColumns.values():
            print(variable)

            
        
        # 
        # for n,sensor in enumerate(self.systemConfiguration.sensorConfigurations.values()):
        #     if 'soinc' in sensor['sensorType']:
        #         if sensor['sensorModel'] in integratedSonics:
        #             i += 1
        #         for key,value in self.template['METADATA']['Instruments'].items():
        #             if key.startswith('instr_n') and value is not None and type(value) is str and value.startswith('sensor['):
        #                 param = value.replace("sensor['",'').replace("']",'')
        #                 if param in sensor:
        #                     paramValue = eval(value)
        #                     if type(paramValue) is str:
        #                         paramValue = paramValue.lower()
        #                 else:
        #                     paramValue = ''
        #                 self.template['METADATA']['Instruments'][key] = paramValue
        #             # elif key.starswith('instr_n') and value is not None and type(value) is str and value.startswith('sensor['):
        #         # Note this includes integrated sonics, which have sensor type "sonic-...."
        #         # if sensor['sensorType'] != 'sonic':
        #         #     for key,value in s

        #     n = n+i
        #     print(n)
        #     # breakpoint()
        # for sec in self.template['METADATA'].keys():
        #     for key,value in self.template['METADATA'][sec].items():
        #         if value is not None and type(value) is str and value.startswith('self.'):
        #             try:
        #                 self.template['METADATA'][sec][key] = eval(value)
        #             except:
        #                 print(value)
        #                 breakpoint()
        # print(self.template['METADATA']['Project'])
        # breakpoint()

    def writeMetadata(self,fileName):
        header = ';GHG_METADATA'