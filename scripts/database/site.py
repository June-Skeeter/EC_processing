import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from scripts.database.project import project,configCommon
from scripts.database.spatiotemporalObjects import pointObject

mdMap = project.metadataMap
@dataclass(kw_only=True)
class site(pointObject,project):
    siteID: str
    def __post_init__(self):
        if self.UID is None:
            self.formatUID('siteID')
        super().__post_init__()
        if not type(self).__name__.endswith('siteConfiguration'):
            print(type(self))
            self.syncConfig(siteConfiguration)

headerText = f'''
Site configuration file defines key site-level site parameters
Values defined here (e.g., startDate) are shared with nested sub-site objects (e.g., dataSource) unless explicitly defined in the dataSourceConfiguration
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class siteConfiguration(configCommon,site):
    header: str = field(default=headerText,repr=False,init=False) # YAML header, must be treated differently
    siteID: str = field(
        metadata=mdMap('Unique siteID code')
    )
    siteName: str = field(
        default = None,
        metadata=mdMap('Name of the Site')
    )
    PI: str = field(
        default = None,
        metadata=mdMap('Principal Investigator(s)')
    )
    description: str = field(
        default = None,
        metadata=mdMap('self explanatory')
    )
    canopyHeight: float = field(
        default=None,
        metadata=mdMap('optional parameter to describe general vegetation height at site.  Can be overridden by dynamic values where appropriate')
    )

    def __post_init__(self):
        self.configName = f"{self.siteID}_siteConfig.yml"
        self.subPath = os.path.sep.join(['siteMetadata',self.siteID])
        self.formatSpaceTimeFields()
        super().__post_init__()
        # if not self.configFileExists or not self.readOnly:
        if not self.readOnly:
            self.saveConfigFile()