import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from scripts.database.project import project
from scripts.database.spatiotemporalObjects import pointObject

default_comment = f'''
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class site(pointObject,project):
    siteID: str
    def __post_init__(self):
        if self.UID is None:
            self.formatUID('siteID')
        super().__post_init__()
        if not type(self).__name__.endswith('siteConfiguration'):
            self.syncConfig(siteConfiguration)

            
@dataclass(kw_only=True)
class siteConfiguration(site):
    header: str = field(default=default_comment,repr=False,init=False) # YAML header, must be treated differently

    fromFile: bool = True
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
    canopyHeight: float = field(
        default=None,
        metadata= {'description':'optional parameter to describe general vegetation height at site.  Can be overridden by dynamic values where appropriate'}
    )
    lastModified: str = field(default=None)
    
    def __post_init__(self):
        self.configName = f"{self.siteID}_siteConfig.yml"
        self.subPath = os.path.sep.join(['siteMetadata',self.siteID])
        self.formatSpaceTimeFields()
        super().__post_init__()
        if not self.configFileExists or not self.readOnly:
            self.saveConfigFile()