import os
from typing import Iterable
from datetime import datetime, timezone
import dataclasses
from dataclasses import dataclass, field, make_dataclass

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
# from modules.helperFunctions.getClasses import getClasses

from src.databaseObjects.defaultObjects import spatialObject

# import src.siteSetup.loggerObjects as loggerObjects
import src.databaseObjects.defaultObjects as defaultObjects
from src.siteSetup.ecSystem import ecSystem
from src.siteSetup.biometSystem import biometSystem


@dataclass(kw_only=True)
class siteObject(spatialObject):
    projectPath: str = field(default=None,repr=False)
    siteID: str = field(
        default = 'siteID',
        metadata = {'description': 'Unique Site Identifier'} 
    )
    siteName: str = field(
        default = None,
        metadata = {'description': 'Name of the Site'} 
    )
    description: str = field(
        default = None,
        metadata = {'description': 'self explanatory'} 
    )
    PI: str = field(
        default = None,
        metadata = {'description': 'Principal Investigator(s)'} 
    )
    dataSystems: Iterable = field(
        default_factory=dict,
    )

    def __post_init__(self):
        if self.projectPath:
            self.configFile = os.path.join(self.projectPath,self.siteID,type(self).__name__+'.yml')
        if not os.path.isfile(self.configFile) and self.safeMode:
            self.safeMode = False
        super().__post_init__()
        self.dataSystems = self.processClassIterable(self.dataSystems,[ecSystem,biometSystem],classKey='systemType')
        if not self.safeMode or not self.configStatus:
            self.saveConfigFile()
        