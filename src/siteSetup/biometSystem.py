import dataclasses
import numpy as np
from typing import Iterable
from dataclasses import dataclass, field, MISSING
from src.databaseObjects.defaultObjects import spatialObject,sensorObject
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class biometSensor(sensorObject):

    def __post_init__(self):
        super().__post_init__()



@dataclass(kw_only=True)
class biometSystem(spatialObject):
    systemID: str
    metSensors: Iterable = field(
        default_factory = list
        )

    def __post_init__(self):
        self.systemID = f"{self.systemID}_BIOMET_{self.index}"
        # Format sensor objects
        if dataclasses.is_dataclass(self.metSensors):
            self.metSensors = [self.metSensors.toConfig()]
        elif type(self.metSensors) is dict:
            self.metSensors = list(self.ecSenmetSensorssors.values())
        for i,sonic in enumerate(self.metSensors):
            if dataclasses.is_dataclass(sonic):
                self.metSensors[i] = sonic.toConfig()

        super().__post_init__()

        for sensor in self.metSensors:
            if sensor['measurementHeight'] is None:
                sensor['measurementHeight'] = self.measurementHeight
            if sensor['northOffset'] is None:
                sensor['northOffset'] = self.northOffset
            sensor = biometSensor.from_dict(sensor)

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