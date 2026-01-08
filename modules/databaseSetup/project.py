import os
import sys
import yaml
from typing import Iterable
from datetime import datetime, timezone
from modules.helperFunctions.parseCoordinates import parseCoordinates

from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass

import modules.helperFunctions.packDict as packDict

# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','configFiles','projectStructure.yml')) as f:
#     structure = yaml.safe_load(f)

# breakpoint()

default_comment = f'''
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str = field(repr=False)
    subPath: str = field(default=None,repr=False,init=False)
    depth: int = field(default=0,init=False,repr=False)

    def __post_init__(self):
        
        if self.projectPath is None:
            return
        if not type(self).__name__.endswith('Configuration'):
            self.syncConfig(projectConfiguration.from_dict(self.__dict__))
        self.rootPath = self.projectPath
        if self.subPath:
            self.rootPath = os.path.join(self.rootPath,self.subPath)
        super().__post_init__()

    def syncConfig(self,config,dbg=False):
        config = config.from_dict(self.to_dict(keepNull=False)|{'projectPath':self.projectPath})
        self.depth+=1
        exclude = list(project.__dataclass_fields__.keys()) + list(baseClass.__dataclass_fields__.keys())
        
        for key,value in config.__dict__.items():
            if (key not in exclude and value is not None 
                and (key not in self.__dict__.keys() or self.__dict__[key] is None)
                ):
                print(key,value)
                self.logMessage('FuckupHere',traceback=True)
                setattr(self,key,value)
        

    def closeProject(self):
        pass

@dataclass(kw_only=True)
class projectConfiguration(project):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated 

    createdBy: str = field(default='')
    lastModified: str = field(default=None)
    projectDescription: str = field(default='')

    def __post_init__(self):
        super().__post_init__()
        
        if os.path.isdir(self.rootPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.rootPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty diretory: {self.rootPath}')

        # Only save if it is first time creating
        # Otherwise saves are performed where appropriate in child classes
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile()


@dataclass(kw_only=True)
class spatialObject(project):
    # A default class for spatially referenced objects
    startDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date of installation. Will parse from string (assuming Year-Month-Day order) For nested values, defaults to parent object, provide to override',
    })
    endDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date of removal (or None). Will parse from string (assuming Year-Month-Day order) For nested values, defaults to parent object, provide to override',
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
        default = 'UTC',
        metadata = {
            'description': 'UTC offset.  For nested values, assumed to be same as parent object.  Optionally to provide if different from parent value.'
    })

    def __post_init__(self):
        if (type(self.latitude) is not self.__dataclass_fields__['latitude'].type or type(self.longitude) is not self.__dataclass_fields__['longitude'].type) and self.typeCheck:
            pC = parseCoordinates(UID=None,latitude=self.latitude, longitude=self.longitude)
            self.latitude, self.longitude = pC.latitude, pC.longitude
        else:
            self.logMessage('Do I want UTM?')
            # breakpoint()
        super().__post_init__()

@dataclass(kw_only=True)
class site(spatialObject):
    siteID: str
    def __post_init__(self):
        super().__post_init__()
        if not type(self).__name__.endswith('siteConfiguration'):
            self.syncConfig(siteConfiguration)


@dataclass(kw_only=True)
class siteConfiguration(site):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated differently

    siteID: str = field(
        metadata = {'description': 'Unique siteID code'} 
    )
    siteName: str = field(
        default = None,
        metadata = {'description': 'Name of the Site'} 
    )
    PI: str = field(
        default = None,
        metadata = {'description': 'Principal Investigator(s)'} 
    )
    description: str = field(
        default = None,
        metadata = {'description': 'self explanatory'} 
    )
    lastModified: str = field(default=None)
    
    def __post_init__(self):
        self.subPath = os.path.sep.join(['configurationFiles',self.siteID])
        super().__post_init__()
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile()
        
@dataclass(kw_only=True)
class source(site):
    sourceID: str
    
    def __post_init__(self):
        super().__post_init__()
        if not type(self).__name__.endswith('sourceConfiguration'):
            self.syncConfig(sourceConfiguration)
@dataclass(kw_only=True)
class sourceConfiguration(source):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated differently

    sourceID: str = field(
        metadata = {'description': 'Unique sourceID code'} 
    )
    systemConfiguration: dict = field(
        default_factory=dict,
        metadata={
            'description':'a system object, which contains information on the system collecting the data'
        })
    sourceFile: Iterable = field(
        default=None,
        metadata={
            'description':'a system object, which contains information on the system collecting the data'
    })
    lastModified: str = field(default=None)

    def __post_init__(self):
        self.subPath = os.path.sep.join(['configurationFiles',self.siteID,self.sourceID])
        super().__post_init__()
        if not self.configFileExists or not self.readOnly:

            self.saveConfigFile(keepNull=False)