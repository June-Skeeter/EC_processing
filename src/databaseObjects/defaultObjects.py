import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field, MISSING

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
# from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.parseCoordinates import parseCoordinates

@dataclass(kw_only=True)
class defaultObject(project):
    startDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date of installation. For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.',
    })
    endDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date of removal (or None). For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    projectPath: str = field(default=None,init=False,repr=False)
    index: int = field(default=1,repr=False)
    UID: str = field(repr=False,init=False)
    linkedID: str = field(repr=False,default=None,init=False)
    
    def __post_init__(self):
        if not hasattr(self, 'UID'):
            self.linkedID = [k for k in self.__dataclass_fields__.keys() if k.endswith('ID')][-1]
            self.UID = self.__dict__[self.linkedID]
        super().__post_init__()
            
    def updateUID(self):
        self.index += 1
        self.UID = f"{self.UID.rsplit('_',1)[0]}_{self.index}"
        self.__dict__[self.linkedID] = self.UID
        
@dataclass(kw_only=True)
class spatialObject(defaultObject):
    # A default class for spatially referenced objects
    # objectType: str = field(default='point',repr=False,init=False)

    latitude: float = field(
        default = None,
        metadata = {
            'description': 'Latitude (WGS1984) Stored in decimal degrees.  Will parse input from other common format. For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    longitude: float = field(
        default = None,
        metadata = {
            'description': 'Longitude (WGS1984) Stored in decimal degrees.  Will parse input from other common format. For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    altitude: float = field(
        default = None,
        metadata = {
            'description': 'Elevation (m.a.s.l).  For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    timezone: str = field(
        default = None,
        metadata = {
            'description': 'UTC offset.  For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })

    def __post_init__(self):
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=None,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        super().__post_init__()

@dataclass(kw_only=True)
class sensorObject(spatialObject):
    keepNull: bool = False
    
    sensorID: str = field(default=None)
    sensorModel: str = field(
        default = None,
        metadata = {
            'description': 'The sensor model, auto-filled from class name',
    })
    name: str = field(
        default = None,
        metadata = {
            'description': 'Custom descriptor variable',
    })
    manufacturer: str = field(
        default = None,
        init=False,
        metadata = {
            'description': 'Indicates manufacturer of sensor, auto from class name',
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial# (if known)',
    })
    sensorType: str
    
    def __post_init__(self):
        if self.sensorModel is None:
            self.sensorModel = type(self).__name__
        if self.serialNumber:
            self.sensorID = f"{self.sensorModel}_{self.serialNumber}"
        elif self.name:
            self.sensorID = f"{self.sensorModel}_{self.name.replace(' ','_')}"
        else:
            self.sensorID = f"{self.sensorModel}_{self.index}"
        super().__post_init__()