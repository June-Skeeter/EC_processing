import os
from datetime import datetime, timezone

from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.helperFunctions.parseCoordinates import parseCoordinates

default_comment = f'''
File Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class projectConfiguration(baseClass):
    verbose: str = None
    projectPath: str
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    dateModified: str = field(default_factory=lambda: datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'))

    def __post_init__(self):
        self.configFilePath = os.path.join(self.projectPath,type(self).__name__+'.yml')
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.projectPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.projectPath}')
        super().__post_init__()
        self.dateModified = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
        if not self.configFileExists:
            self.saveConfigFile()


@dataclass(kw_only=True)
class spatialObject(baseClass):
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

    def __post_init__(self):
        if type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type:
            pC = parseCoordinates(UID=None,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        super().__post_init__()


@dataclass(kw_only=True)
class siteConfiguration(spatialObject):
    sitePath: str = field(init=False,repr=False)
    projectPath: str = field(repr=False)
    siteID: str
    latitude: float = field()
    longitude: float = field()
    
    def __post_init__(self):
        projectConfiguration(projectPath=self.projectPath)
        self.sitePath = os.path.join(self.projectPath,self.siteID)
        self.configFilePath = os.path.join(self.sitePath,type(self).__name__+'.yml')
        super().__post_init__()
        self.saveConfigFile(keepNull=False)
