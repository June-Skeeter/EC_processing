import os
from typing import Iterable
from datetime import datetime, timezone
from dataclasses import dataclass, field, make_dataclass

from src.databaseObjects.project import project

from modules.helperFunctions.dictFuncs import dcToDict
from modules.helperFunctions.getClasses import getClasses

from src.databaseObjects.spatialObject import spatialObject

# Get all defined loggers
import src.readData.dataSource as dataSource
dataSource = getClasses(dataSource)
dataSource = {cl.__name__:cl for cl in dataSource[::-1]}

# Get all defined sensors
import src.siteSetup.sensorObjects as sensorObjects
sensorObjects = getClasses(sensorObjects)
sensorObjects = {cl.__name__:cl for cl in sensorObjects[::-1]}

@dataclass(kw_only=True)
class siteMetadata(spatialObject):
    projectPath: str = field(default=None,repr=False)
    validate: bool = field(
        repr=False,
        default=True
    )
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
        if self.projectPath:
            self.configFile = os.path.join(self.projectPath,self.siteID,type(self).__name__+'.yml')
        super().__post_init__()
        if self.validate:
            self.dataSources = self.parseNestedObjects(
                objectsToParse=self.dataSources,
                objectOptions = dataSource,
                objectID = 'model')
            if self.configFile:
                print('>?')
                breakpoint()
                self.saveConfigFile(inheritance=True)
    
    def config(self):
        return dcToDict(self,repr=True,inheritance=True)


@dataclass(kw_only=True)
class getSite(project):
    siteID: str
    siteMetadata: dict = field(init=False)

    def __post_init__(self):
        cfg = os.path.join(self.projectPath,self.siteID,'siteMetadata.yml')
        self.siteMetadata = siteMetadata(configFile=cfg,siteID=self.siteID,validate=False).config()
        