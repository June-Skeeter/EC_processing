import dataclasses
import numpy as np
from typing import Iterable
from dataclasses import dataclass, field, MISSING
from src.databaseObjects.defaultObjects import systemObject,sensorObject
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class biometSensor(sensorObject):

    def __post_init__(self):
        super().__post_init__()



@dataclass(kw_only=True)
class biometSystem(systemObject):
    # placeholder: str = None

    def __post_init__(self):

        super().__post_init__()

        sensorDict = {}
        for sensor in self.sensors:
            sensor = biometSensor.from_dict(sensor)
            while sensor.UID in sensorDict.keys():
                sensor.updateUID()
            sensorDict[sensor.UID] = sensor.toConfig(keepNull=False)
        self.sensors = sensorDict

@dataclass(kw_only=True)
class thermocouple(biometSensor):
    sensorType: str = 'thermocouple'
    pass

@dataclass(kw_only=True)
class SN500(biometSensor):
    manufacturer: str = 'Apogee'
    sensorType: str = 'net-radiometer'

@dataclass(kw_only=True)
class HMP(biometSensor):
    manufacturer: str = 'Vaisala'
    sensorType: str = 'temperature-humidity'

@dataclass(kw_only=True)
class voltage(biometSensor):
    pass