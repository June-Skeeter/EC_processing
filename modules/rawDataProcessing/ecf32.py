import configparser
from modules.helperFunctions.baseClass import baseClass
from modules.databaseSetup.configurations import dataSourceConfiguration
from dataclasses import dataclass, field
# from pathlib import path
import numpy as np
import time
import yaml
import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','metadata_eddypro_map.yml')) as f:
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

        self.metadataFilePath = os.path.join(self.configFileRoot,'ecf32.metadata')
        self.eddyproFilePath = os.path.join(self.configFileRoot,'ecf32.eddypro')

        # Use eval statements to fill dynamic variables
        # both .metadata and .eddypro files should be created
        self.generateMetaDataFile()
        self.generateEddyProFile()
        
        metadata = configparser.ConfigParser()
        for sec in self.metadataFile.keys():
            metadata.add_section(sec)
            for key,value in self.metadataFile[sec].items():
                metadata[sec][key]=str(value)
        with open(self.metadataFilePath,'w') as f:
            f.write(';GHG_METADATA\n')
            metadata.write(f,space_around_delimiters=False)

        eddypro = configparser.ConfigParser()
        for sec in self.eddyproFile.keys():
            eddypro.add_section(sec)
            for key,value in self.eddyproFile[sec].items():
                eddypro[sec][key]=str(value)
        with open(self.eddyproFilePath,'w') as f:
            f.write(';EDDYPRO_PROCESSING\n')
            eddypro.write(f,space_around_delimiters=False)
        
        # print(self.metadataFile)

    def generateMetaDataFile(self):

        # Fill these simple paramters fist
        for sec in ['Project','Files','Site','Station','Timing']:
            self.metadataFile[sec] = {}
            for key,value in self.template['METADATA'][sec].items():
                self.metadataFile[sec][key] = self.parseSelf(value)

        # Next process intruments
        # Bellow is intenteded for "simple" setup with one sonic & corresponding IRGAS
        # Eddy-pro "supports" defining sonics, but all flux calculations are done based one reference sonic, so secondary sonics give littel extra info
        # Extension to multi-sonic setups could be made but would require minor edits here, and major eddits to EddyPro source code
        
        def parseSensor(value,sensor):
            if type(value) is str and value.startswith('sensor['):
                param = value.split("sensor['")[-1].split("']")[0]
                if param in sensor:
                    value = eval(value)
                    if type(value) is str:
                        value = value.lower()
                else:
                    value = None
            if value is None:
                value = ''
            print(value)
            return(value)

        i = 1
        self.metadataFile['Instruments'] = {}
        for sensor in self.systemConfiguration.sensorConfigurations.values():
            for key,value in self.template['METADATA']['Instruments'].items():
                self.metadataFile['Instruments'][key.replace('_n_',f"_{i}_")] = parseSensor(value,sensor)
            if 'sonic' in sensor['sensorType'] and sensor['sensorModel'] in self.integratedSonics:
                for key,value in self.template['METADATA']['Instruments'].items():
                    self.metadataFile['Instruments'][key.replace('_n_',f"_{i+1}_")] = parseSensor(value,sensor)
            if 'sonic' in sensor['sensorType'] and sensor['sensorModel'] in self.integratedSonics:
                i += 2
            else:
                i += 1
        

        def parseVariable(value,variable):
            if type(value) is str and value.startswith('variable['):
                param = value.split("variable['")[-1].split("']")[0]
                if param in variable:
                    value = eval(value)
                    if type(value) is str:
                        value = value.lower()
                else:
                    value = None
            if value is None:
                value = ''
            return(value)

        i = 1
        self.metadataFile['FileDescription'] = {key:self.parseSelf(value) for key,value in self.template['METADATA']['FileDescription'].items() if not key.startswith('col_n')}
        for variable in self.sourceFileConfiguration.dataColumns.values():
            if variable['dtype'] == '<f4' and not variable['ignore']:
                for key,value in self.template['METADATA']['FileDescription'].items():
                    self.metadataFile['FileDescription'][key.replace('_n_',f'_{i}_')] = parseVariable(value,variable)
                i += 1
            else:
                self.sourceFileConfiguration.dataColumns[variable['variableNameIn']]['ignore'] = True

    def generateEddyProFile(self):
        
        # Fill these simple paramters fist
        for sec in ['Project','FluxCorrection_SpectralAnalysis_General','RawProcess_General','RawProcess_Settings','RawProcess_Tests','RawProcess_ParameterSettings','RawProcess_TiltCorrection_Settings','RawProcess_TimelagOptimization_Settings','RawProcess_BiometMeasurements','RawProcess_WindDirectionFilter']:
            self.eddyproFile[sec] = {}
            for key,value in self.template['EDDYPRO'][sec].items():
                self.eddyproFile[sec][key] = self.parseSelf(value)

    def parseSelf(self,value):
        if value is not None and type(value) is str and value.startswith('self.'):
            value = eval(value)
        if value is None:
            value = ''
        return(value)
        
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