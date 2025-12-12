from datetime import datetime
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.parseCoordinates import parseCoordinates

@dataclass(kw_only=True)
class UID(baseClass):
    # verbose: bool = field(default=False,repr=False)
    index: int = field(default=1,init=False,repr=False)
    UID: str = field(default=None,repr=False)
    UID_source: str = field(default=None,init=False,repr=False)
    UID_name: str = field(default=None,init=False,repr=False)

    def __post_init__(self):
        if self.UID_source is None and self.UID_name is not None:
            self.UID_source = self.UID_name
        elif self.UID_name is None and self.UID_source is not None:
            self.UID_name = self.UID_source
        if self.UID is None and self.UID_source is not None:
            self.UID = f"{getattr(self,self.UID_source)}_{self.index}"
            setattr(self,self.UID_name,self.UID)
        elif self.UID is not None:
            self.index = int(self.UID.rsplit('_',1)[-1])
        super().__post_init__()

    def updateUID(self):
        self.index += 1
        self.UID = f"{getattr(self,self.UID_name)}_{self.index}"
        setattr(self,self.UID_name,self.UID)

@dataclass(kw_only=True)
class spatialObject(UID):
    # A default class for spatially referenced objects
    # objectType: str = field(default='point',repr=False,init=False)

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
    description: str = field(
        default = None,
        metadata = {'description': 'self explanatory'} 
    )

    def __post_init__(self):
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=None,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        super().__post_init__()
