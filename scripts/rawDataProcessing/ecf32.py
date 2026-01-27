import configparser
from scripts.database.dataSource import dataSource
from scripts.rawDataProcessing.rawFile import sourceFile
from dataclasses import dataclass, field
from datetime import datetime
# from pathlib import path
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import numpy as np
import time
import yaml
import os

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','metadata_eddypro_map.yml')) as f:
    metadataMap = yaml.safe_load(f)


@dataclass(kw_only=True)
class ecf32(dataSource):
    # siteID: str
    # dataSourceID: str
    fileName: str
    template: dict = field(default_factory=lambda:metadataMap)
    metadataFile: dict = field(default_factory=dict)
    f32Files: list = field(default_factory=list)
    eddyproFile: dict = field(default_factory=dict)
    defaultInterval: int = 30
    integratedSonics: list = field(default_factory=lambda:['IRGASON'])
    configName: str = field(default='dataSourceConfiguration.yml',repr=False,init=False)

    def __post_init__(self):
        # self.subPath = os.path.sep.join(['siteMetadata',self.siteID,self.dataSourceID])

        T1 = time.time()
        super().__post_init__()
        #Reset rootpath to save outputs to highFrequencyDataFolder location
        self.subPath = os.path.sep.join(['highFrequencyData',self.siteID,self.dataSourceID])
        self.rootPath = os.path.join(self.projectPath,self.subPath)
        os.makedirs(self.rootPath,exist_ok=True)
        self.metadataFilePath = os.path.join(self.rootPath,'ecf32.metadata')
        self.eddyproFilePath = os.path.join(self.rootPath,'ecf32.eddypro')

        # Use eval statements to fill dynamic variables
        # both .metadata and .eddypro files should be created
        self.generateMetaDataFile()
        self.generateBinaryFile()
        self.generateEddyProFile()
        self.logMessage(f"Time Elapsed generating f32 file{time.time()-T1}")
               

    def generateMetaDataFile(self):

        # Fill these simple paramters fist
        for sec in ['Project','Files','Site','Station','Timing']:
            self.metadataFile[sec] = {}
            for key,value in self.template['METADATA'][sec].items():
                try:
                    self.metadataFile[sec][key] = self.parseSelf(value)
                except:
                    self.logError('Error in f32 variable assignment')

        # Next process instruments
        # Bellow is intended for "simple" setup with one sonic & corresponding IRGAS
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
            return(value)

        i = 1
        self.metadataFile['Instruments'] = {}
        for sensor in self.sourceSystemMetadata['sensorConfigurations'].values():
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
            if value is None:
                value = ''
            elif type(value) is str and 'variable[' in value:
                param = value.split("variable['")[-1].split("']")[0]
                if param in variable:
                    # check if value is empty:
                    if len(variable[param]):
                        value = eval(value)
                        if type(value) is str:
                            value = value.lower()
                    else:
                        value = ''
                else:
                    value = ''
            else:
                print(value)
                print('issue?')
                breakpoint()
            return(value)

        i = 1
        self.metadataFile['FileDescription'] = {key:self.parseSelf(value) for key,value in self.template['METADATA']['FileDescription'].items() if not key.startswith('col_n')}
        for variable in self.sourceFileMetadata['traceMetadata'].values():
            if variable['dtype'] == '<f4' and not variable['ignore']:
                for key,value in self.template['METADATA']['FileDescription'].items():
                    self.metadataFile['FileDescription'][key.replace('_n_',f'_{i}_')] = parseVariable(value,variable)
                i += 1
            else:
                self.sourceFileMetadata['traceMetadata'][variable['variableName']]['ignore'] = True

        metadata = configparser.ConfigParser()
        for sec in self.metadataFile.keys():
            metadata.add_section(sec)
            for key,value in self.metadataFile[sec].items():
                metadata[sec][key]=str(value)
        with open(self.metadataFilePath,'w') as f:
            f.write(';GHG_METADATA\n')
            metadata.write(f,space_around_delimiters=False)

    def generateBinaryFile(self):
        # kwargs = self.sourceFileMetadata.to_dict()
        data,timestamp = sourceFile(fileName=self.fileName,fileFormat=self.sourceFileMetadata['fileFormat'],kwargs=self.sourceFileMetadata).parseFile()
        keep = [value['variableName'] for value in self.sourceFileMetadata['traceMetadata'].values() if not value['ignore']]
        maxN = int(self.metadataFile['Timing']['acquisition_frequency']*self.metadataFile['Timing']['file_duration']*60)
        splits = int(np.ceil(data.shape[0]/maxN))
        for i in range(splits):
            sub = data.iloc[i*maxN:(i+1)*maxN]
            fn = timestamp['datetime'].iloc[i*maxN].strftime('%Y%m%dT%H%M%S.f32')
            filepath = os.path.join(self.rootPath,fn)
            sub[keep].values.T.flatten().astype('float32').tofile(filepath)
            self.f32Files.append(filepath)

    def generateEddyProFile(self):
        
        # Fill these simple paramters fist
        for sec in ['Project','FluxCorrection_SpectralAnalysis_General','RawProcess_General','RawProcess_Settings','RawProcess_Tests','RawProcess_ParameterSettings','RawProcess_TiltCorrection_Settings','RawProcess_TimelagOptimization_Settings','RawProcess_BiometMeasurements','RawProcess_WindDirectionFilter']:
            self.eddyproFile[sec] = {}
            for key,value in self.template['EDDYPRO'][sec].items():
                self.eddyproFile[sec][key] = self.parseSelf(value)
                

        eddypro = configparser.ConfigParser()
        for sec in self.eddyproFile.keys():
            eddypro.add_section(sec)
            for key,value in self.eddyproFile[sec].items():
                eddypro[sec][key]=str(value)
        with open(self.eddyproFilePath,'w') as f:
            f.write(';EDDYPRO_PROCESSING\n')
            eddypro.write(f,space_around_delimiters=False)

    def parseSelf(self,value):
        if value is not None and type(value) is str and value.startswith('self.'):
            value = eval(value)
        if value is None:
            value = ''
        return(value)
        