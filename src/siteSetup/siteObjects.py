import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field, make_dataclass

from ..dbFunctions.project import project

from ..helperFunctions.dictFuncs import dcToDict
from ..helperFunctions.getClasses import getClasses

from src.siteSetup.defaultObject import defaultObject

# Get all defined loggers
import src.siteSetup.dataSource as dataSource
dataSource = getClasses(dataSource)
dataSource = {cl.__name__:cl for cl in dataSource[::-1]}

# Get all defined sensors
import src.siteSetup.sensorObjects as sensorObjects
sensorObjects = getClasses(sensorObjects)
sensorObjects = {cl.__name__:cl for cl in sensorObjects[::-1]}




@dataclass(kw_only=True)
class siteMetadata(defaultObject):
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
    dataSources: Iterable = field(
        default_factory = lambda:[
            dataSource['dataLogger']
            ],
        metadata = {
            'description': 'Inventory of data sources for site',
            'options':{name:value.template() for name,value in dataSource.items()}
    })

    def __post_init__(self):
        self.UID = self.siteID
        super().__post_init__()
        self.dataSources = self.parseNestedObjects(
            objectsToParse=self.dataSources,
            objectOptions = dataSource,
            objectID = 'model')
        if self.configFile:
            self.saveToYaml(inheritance=True)
            self.logWarning('Rename saveToYaml')


# @dataclass(kw_only=True)
# class siteSetup(project):
#     siteID: str
#     siteMetadata: dict = field(init=False)

#     def __post_init__(self):
#         cfg = os.path.join(self.projectPath,self.siteID,'siteMetadata.yml')
#         sM = siteMetadata(configFile=cfg,siteID=self.siteID)
#         self.siteMetadata = dcToDict(sM,inheritance=False)
        