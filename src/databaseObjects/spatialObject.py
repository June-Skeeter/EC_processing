import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field, MISSING

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
# from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.parseCoordinates import parseCoordinates


@dataclass(kw_only=True)
class spatialObject(project):
    # A default class for spatially referenced objects
    projectPath: str = field(default=None,init=False,repr=False)
    objectType: str = field(default='point',repr=False,init=False)
    index: int = field(default=1,repr=False,init=False)
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
        if not hasattr(self, 'UID'):
            self.linkedID = [k for k in self.__dataclass_fields__.keys() if k.endswith('ID')][-1]
            self.UID = self.__dict__[self.linkedID]
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=self.UID,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        super().__post_init__()
        # self.updateUID()

    def updateUID(self):
        self.index += 1
        self.UID = f"{self.UID.rsplit('_',1)[0]}_{self.index}"
        self.__dict__[self.linkedID] = self.UID

    # def parseNestedObjects(self, objectsToParse, objectOptions, objectID):
    #     nest = {}
    #     if type(objectsToParse) is dict:
    #         objectsToParse = list(objectsToParse.values())
    #     for obj in objectsToParse:
    #         if type(obj) is dict:
    #             kwargs = obj.copy()
    #             print(obj)
    #             classObject = objectOptions[obj[objectID]]
    #             obj = classObject.from_dict(kwargs)
    #         else:
    #             pass
    #         while obj.UID in nest.keys():
    #             obj.updateUID()
    #         nest[obj.UID] = dcToDict(obj,repr=True,keepNull=False)
    #     return (nest)
           

    @classmethod
    def template(cls):
        template = {}
        for k,v in cls.__dataclass_fields__.items():
            if v.repr:
                desc = {'datatype':v.type.__name__,}
                if 'description' in v.metadata:
                    desc['description'] = v.metadata['description']
                if 'options' in v.metadata:
                    desc['options'] = v.metadata['options']
                template[k] = desc
        return(template)
