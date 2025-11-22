from typing import Iterable
from dataclasses import dataclass, field, make_dataclass

from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.parseCoordinates import parseCoordinates

# from src.siteSetup.sensorList import *
from src.siteSetup.loggerList import *


@dataclass(kw_only=True)
class defaultObject(baseFunctions):
    index: int = field(default=0,repr=False,init=False)
    UID: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None

    def __post_init__(self):
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=self.UID,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        if self.latitude is None or self.longitude is None:
            self.__dataclass_fields__['latitude'].repr = False
            self.__dataclass_fields__['longitude'].repr = False
        super().__post_init__()
        if self.UID is None:
            self.updateUID()

    def updateUID(self):
        self.index += 1
        self.UID = f"{type(self).__name__}_{self.index}"


@dataclass(kw_only=True)
class nestedObjects(defaultObject):

    def parseNestedObjects(self, nestedObjects, classID):
        nest = {}
        if type(nestedObjects) is dict:
            nestedObjects = list(nestedObjects.values())
        for obj in nestedObjects:
            if type(obj) is dict:
                kwargs = obj.copy()
                classObject = eval(obj[classID])
            else:
                kwargs = obj.__dict__
                classObject = type(obj)
            dcFields = classObject.__dataclass_fields__
            dcFields = [(name,dcFields[name].type,dcFields[name])for name in classObject.__annotations__]
            if hasattr(classObject,'__pre_init__'):
                namespace = {'__pre_init__': classObject.__pre_init__}
            else:
                namespace = None
            classObject = make_dataclass(
                cls_name = classObject.__name__, 
                fields = dcFields,
                bases = (defaultObject,),
                namespace = namespace,
                kw_only=True
                )
            obj = classObject.from_dict(kwargs)
            while obj.UID in nest.keys():
                obj.updateUID()
            nest[obj.UID] = obj
            print('dump2dict')
        return (nest)


@dataclass(kw_only=True)
class siteMetadata(nestedObjects):
    siteName: str = None
    description: str = None
    PI: str = None
    startDate: str = None
    endDate: str = None
    timezone: str = None
    measurementInventory: Iterable = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.measurementInventory = self.parseNestedObjects(self.measurementInventory,'model')
