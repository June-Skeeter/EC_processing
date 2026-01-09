from dataclasses import dataclass, field
from modules.helperFunctions.parseCoordinates import parseCoordinates

@dataclass(kw_only=True)
class spatialObject():
    UID: str = field(default=None,repr=False)
    latitude: list = None
    longitude: list = None

    def spatialObject(self):
        if self.latitude is not None and self.longitude is not None:
            pC = parseCoordinates(UID=self.UID,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude

    def formatUID(self,UID=None):
        if self.UID is None:
            self.UID = getattr(self,UID)
        if '_' not in self.UID or not self.UID.split('_')[-1].isnumeric():
            self.UID = self.UID + '_1'

    def updateUID(self):
        if '_' in self.UID and self.UID.split('_')[-1].isnumeric():
            index = int(self.UID.split('_')[-1])+1
            self.UID = self.UID.rsplit('_',1)[0]+'_'+str(index)
        else:
            self.formatUID()


@dataclass(kw_only=True)
class pointObject(spatialObject):
    latitude: float = field(
        default = None,
        metadata = {
            'description': 'Latitude (WGS1984) stored in decimal degrees.  Will parse input from other common format. For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    longitude: float = field(
        default = None,
        metadata = {
            'description': 'Longitude (WGS1984) stored in decimal degrees.  Will parse input from other common format. For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
    altitude: float = field(
        default = None,
        metadata = {
            'description': 'Elevation (m.a.s.l).  For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })
