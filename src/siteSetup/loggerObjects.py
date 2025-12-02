from typing import Iterable
import dataclasses
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass

# from src.databaseObjects.defaultObjects import spatialObject

from modules.helperFunctions.dictFuncs import dcToDict


# import src.siteSetup.sensorObjects as sensorObjects

@dataclass(kw_only=True)
class dataLogger(baseClass):
    loggerModel: str = field(
        init=False,
        metadata = {
            'description': 'The logger model, auto-filled from class name',
    })
    stationName: str = field(
        default = None,
        metadata = {
            'description': 'Custom descriptor variable',
    })
    manufacturer: str = field(
        default = None,
        metadata = {
            'description': 'Self explanitory',
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial# (if known)',
    })
    fileType: str = field(
        default=None,
        metadata={'description':'Type of file associated with the logger/system'}
    )

    def __post_init__(self):
        self.loggerModel = type(self).__name__

@dataclass(kw_only=True)
class CR1000X(dataLogger):
    manufacturer: str = field(default='Campbell Scientific')

@dataclass
class HOBO(dataLogger):
    manufacturer: str = field(default='Onset')
    fileType: str = field(default='csv')