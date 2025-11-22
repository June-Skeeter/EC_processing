from dataclasses import dataclass, field, MISSING, make_dataclass
from typing import Iterable
from ..helperFunctions.parseCoordinates import parseCoordinates
from ..helperFunctions.baseFunctions import baseFunctions
from datetime import datetime, timezone
from .sensorList import *
from .loggerList import *

def inventoryCheck(inventory):
    cleanInventory = {}
    if type(inventory) is dict:
        inventory = list(inventory.values())
    for obj in inventory:
        print(inventory)
        if type(obj) is dict:
            claxx = eval(obj['UID'].rsplit('_')[0])
            fields = [(name,claxx.__dataclass_fields__[name].type,claxx.__dataclass_fields__[name]) for name in claxx.__annotations__]
            # make_dataclass(obj['UID'],fields=)
            breakpoint()
        for k,v in obj.__dict__.items():
            if v is None and k in pointObject.__dict__.keys():
                setattr(obj, k, pointObject.__dict__[k])
        i = 2
        while obj.UID in cleanInventory.keys():
            obj.generateUID(i)
            i+=1
        cleanInventory[obj.UID] = obj.__dict__
    return cleanInventory
            

@dataclass(kw_only=True)
class pointObject(baseFunctions):
    UID: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None

    def __post_init__(self):
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=self.UID,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        super().__post_init__()
        if self.UID is None:
            self.generateUID()

    def generateUID(self,i=1):
        self.UID = f"{type(self).__name__}_{i}"
        

@dataclass(kw_only=True)
class siteMetadata(pointObject):
    siteName: str = None
    description: str = None
    PI: str = None
    startDate: datetime = None
    endDate: datetime = None
    description: str = None
    timezone: str = 'GMT+7'
    measruementInventory: Iterable = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.measruementInventory = inventoryCheck(self.measruementInventory)
        
        print('okay now?')

# @dataclass(kw_only=True)
# class dataLogger(pointObject):
#     # model: str = None
#     # sensorInventory: Iterable = field(default_factory=dict)

#     def __post_init__(self):
#         super().__post_init__()
#         # breakpoint()
#         self.sensorInventory = inventoryCheck(sensor,self.sensorInventory)

# @dataclass(kw_only=True)
# class sensor(pointObject):
    
#     def __post_init__(self):
#         super().__post_init__()