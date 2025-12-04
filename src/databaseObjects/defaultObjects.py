import os
import dataclasses
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field, MISSING

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
# from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.parseCoordinates import parseCoordinates

@dataclass(kw_only=True)
class defaultObject(project):
    projectPath: str = field(default=None,init=False,repr=False)
    index: str = field(default='1',repr=False)
    UID: str = field(repr=False,init=False)
    linkedID: str = field(repr=False,default=None,init=False)
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
    
    def __post_init__(self):
        if not hasattr(self, 'UID'):
            self.linkedID = [k for k,v in self.__dataclass_fields__.items() if k.endswith('ID') and v.repr][0]
            self.UID = self.__dict__[self.linkedID]
        super().__post_init__()
            
    def updateUID(self):
        if int(self.int):
            self.index = str(int(self.index)+1)
        else:
            if len(self.index.split('_'))>1:
                self.index = self.index.split('_')
                self.index[1] = int(self.index)+1
                self.index = f"{self.index[0]}_{self.index[1]}"
            else:
                self.index = f"{self.index[0]}_1"
    
        self.UID = f"{self.UID.rsplit('_',1)[0]}_{self.index}"
        self.__dict__[self.linkedID] = self.UID

    def formatClassIterables(self,iterables):
        # If dict convert to list for processing
        if type(iterables) is dict:
            iterables = list(iterables.values())
        # If list contains any project-specific dataclass objects, convert to dicts for processing
        for i,iter in enumerate(iterables):
            if dataclasses.is_dataclass(iter):
                # get dict if initialized as dataclass
                iterables[i] = iter.toConfig()
        return(iterables)
    
    def processClassIterable(self,iterables,classMethod,classKey = None,keepNull = False):
        #Given an iterable of dataclasses, format as list dicts, then re-process and output as dict of dicts
        dictOut = {}
        iterables = self.formatClassIterables(iterables=iterables)
        for iter in iterables:
            for key in self.__annotations__:
                if key not in iter or iter[key] is None:
                    iter[key] = getattr(self,key)
            if dataclasses.is_dataclass(classMethod):
                iter = classMethod.from_dict(iter)
            elif dataclasses.is_dataclass(classMethod) and classKey is None:
                self.logError('missing classKey for processing when classMethod is list')
            else:
                clM = classMethod[[i for i,c in  enumerate(classMethod) if  c.__dataclass_fields__[classKey].default == iter[classKey]][0]]
                iter = clM.from_dict(iter)
            while iter.UID in dictOut.keys():
                iter.updateUID()
            dictOut[iter.UID] = iter.toConfig(keepNull=keepNull)
        return (dictOut)
    
    
@dataclass(kw_only=True)
class sourceObject(defaultObject):
    siteID: str = field(default=None,repr=False)
    systemID:
    pass
                
        
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
class systemObject(spatialObject):
    keepNull: bool = field(default = False, repr = False)   
    systemID: str = field(default=None) 
    siteID: str = field(default=None)
    systemType: str = field(default=None)
    dataLogger: Iterable
    sensors: Iterable = field(
        default_factory = list
        )

    def __post_init__(self):
        if self.systemID is not None:
            sysID = self.systemID.split('_')
            self.siteID = sysID[0]
            self.index = sysID[1]
        else:
            self.index = f"{self.systemType}_{self.index}"
            self.systemID = f"{self.siteID}_{self.index}"

        if self.systemType is None:
            self.systemType = type(self).__name__
        self.index = self.systemType
        # self.sensors = self.formatClassIterables(self.sensors)
        super().__post_init__()


@dataclass(kw_only=True)
class sensorObject(spatialObject):
    keepNull: bool = field(default = False, repr = False)    
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
        metadata = {
            'description': 'Indicates manufacturer of sensor, auto from class name',
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial# (if known)',
    })
    sensorType: str = field(default=None,repr=False)
    
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
