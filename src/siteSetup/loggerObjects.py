from typing import Iterable
import dataclasses
from dataclasses import dataclass, field

from src.databaseObjects.defaultObjects import spatialObject

from modules.helperFunctions.dictFuncs import dcToDict


import src.siteSetup.sensorObjects as sensorObjects

@dataclass(kw_only=True)
class dataLogger(spatialObject):
    loggerID: str = field(default=None,init=False)
    loggerModel: str = field(
        init=False,
        metadata = {
            'description': 'The logger model, auto-filled from class name',
    })
    name: str = field(
        default = None,
        metadata = {
            'description': 'Custom descriptor variable',
    })
    
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial# (if known)',
    })
    sensors: Iterable = field(
        default_factory=dict,
        metadata={
            'description':'Inventory of sensors assoicated with a logger'
        }
    )

    def __post_init__(self):
        self.loggerModel = type(self).__name__
        if self.serialNumber:
            self.loggerID = f"{self.loggerModel}_{self.serialNumber}"
        elif self.name:
            self.loggerID = f"{self.loggerModel}_{self.name.replace(' ','_')}"
        else:
            self.loggerID = f"{self.loggerModel}_{self.index}"
        super().__post_init__()
        self.sensors = self.parseSensors()

    def parseSensors(self):
        cleanSensors = {}
        if type(self.sensors) is dict:
            self.sensors = list(self.sensors.values())
        for obj in self.sensors:
            if dataclasses.is_dataclass(obj):
                obj = dcToDict(obj,repr=True,inheritance=True)
            if 'sensorModel' not in obj or not hasattr(sensorObjects,obj['sensorModel']):
                self.logError(f'Not a valid sensorObject: {obj}')
            else:
                kwargs = obj
                sensor = getattr(sensorObjects,obj['sensorModel'])
                sensor = sensor.from_dict(kwargs)
                while sensor.sensorID in cleanSensors.keys():
                    sensor.updateUID()
                cleanSensors[sensor.sensorID] = dcToDict(sensor,inheritance=False)|dcToDict(sensor,keepNull=False)
        return(cleanSensors)


@dataclass(kw_only=True)
class CR1000x(dataLogger):
    manufacturer: str = 'CSI'


@dataclass
class HOBO(dataLogger):
    manufacturer: str = 'Onset'
    fileType: str = 'csv'