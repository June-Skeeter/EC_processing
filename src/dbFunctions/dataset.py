from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict
from .sensor import callSensor

supportedFileFormats = ['TOB3','TOA5','CSV']

@dataclass(kw_only=True)
class dataset(baseFunctions):
    sourceID: str = field(
        default = None,
        metadata = {
            'description': 'Unique ID for data source',
    })
    sourceType: str = field(
        metadata={
            'description': 'Type of raw data',
            'options': ['Flux','Met','Model','Manual','Clean']
    })
    sourceFileFormat: str = field(
        metadata={
            'description': 'Indicates the type of files the inputs are drawn from',
            'options': supportedFileFormats
    })
    startDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date sensor was installed',
    })
    endDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date sensor was removed'
    })
    latitude: str = field(
        default = None,
        metadata = {
            'description': 'Can give more detail if different from site-coordinates.'
    })
    longitude: str = field(
        default = None,
        metadata = {
            'description': 'Can give more detail if different from site-coordinates.'
    })


    def __post_init__(self):
        self.UID()
        super().__post_init__()
    
    def UID(self,i=1):
        self.sourceID = f"{type(self).__name__}_{i}"

@dataclass(kw_only=True)
class externalModel(dataset):
    sourceType: str = 'Model'
    modelName: str

@dataclass(kw_only=True)
class manualMeasurement(dataset):
    sourceType: str = 'Manual'
    name: str

supportedLoggers = ['CR1000','CR1000x','Smart-Flux','Hobo']

@dataclass(kw_only=True)
class loggerMeasurement(dataset):
    manufacturer: str = field(
        default = None,
        metadata = {
            'description': 'Indicates manufacturer of sensor',
    })
    model: str = field(
        default = None,
        metadata = {
            'description': 'The sensor model',
            'options':supportedLoggers
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial no (if known)',
    })
    programHistory: Iterable = field(
        default_factory=dict,
    )
    sensorInventory: Iterable = field(
        default_factory=dict
    )

    def __post_init__(self):
        if self.typeCheck:
            self.sensorCheck()
        super().__post_init__()
    
    def sensorCheck(self):
        if type(self.sensorInventory) is dict:
            self.sensorInventory = list(self.sensorInventory.values())
        Inventory = {}
        for sensorData in self.sensorInventory:
            if type(sensorData) is dict:
                sensorData = callSensor(sensorData['sensorID'])(**sensorData)
                print(sensorData.model)
            i = 2
            while sensorData.sensorID in Inventory.keys():
                sensorData.UID(i)
                i+=1
                
            if sensorData.startDate is None:
                self.logWarning(f'No installation date provided for {sensorData.sensorID}')
                sensorData.startDate = self.startDate
            Inventory[sensorData.sensorID] = dcToDict(sensorData,inheritance=True,repr=True)
        self.sensorInventory = Inventory


@dataclass(kw_only=True)
class CR1000x(loggerMeasurement):
    model: str = 'CR1000x'
    manufacturer: str = 'CSI'
    sourceFileFormat: str = 'TOB3'

@dataclass(kw_only=True)
class HOBO(loggerMeasurement):
    model: str = 'HOBO'
    manufacturer: str = 'Onset'
    sourceType: str = 'Met'
    sourceFileFormat: str = 'CSV'

    
supportedDataSets = ['CR1000x','HOBO']
#################

def callDataset(UID):
    allSensors = {s:eval(s) for s in supportedDataSets}
    print(UID)
    ID = UID.rsplit('_',1)[0]
    return(allSensors[ID])
