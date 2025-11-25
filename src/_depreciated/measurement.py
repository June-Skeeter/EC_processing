# import os
# from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseClass import baseClass
from ..helperFunctions.dictFuncs import dcToDict

default_comment = f'''
Measurement configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class dataSet(baseClass):
    dataSetType: str = field(
        metadata={
            'description': 'Type of raw data',
            'options': ['Flux','Met','Model','Manual','Clean']
    })
    startDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date sensor was installed',
    })
    endDate: datetime = field(
        default = None,
        metadata = {
            'description': 'Date sensor was removed'
    })
    latitude: str = field(
        default = None,
        metadata = {
            'description': 'Can give more detail if different from site-coordinates.'
    })
    longitude: str = field(
        metadata = {
            'description': 'Can give more detail if different from site-coordinates.'
    })


@dataclass(kw_only=True)
class modelData(dataSet):
    dataSetType: str = 'model'

# All observations/measurements have a logger, even if the logger is human :)
@dataclass(kw_only=True)
class logger(dataSet):
    loggerID: str = None
    pass

@dataclass(kw_only=True)
class Manual(logger):
    dataSetType: str = 'model'


supportedLoggers = ['CR1000','CR1000x','Smart-Flux','Hobo']

@dataclass(kw_only=True)
class dataLogger(logger):
    manufacturer: str = field(
        default = None,
        metadata = {
            'description': 'Indicates manufacturer of sensor',
    })
    model: str = field(
        default = None,
        metadata = {
            'description': 'The sensor model',
            'options':supportedLoggers
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial no (if known)',
    })
    programHistory: dict = field(
        default_factory=dict,
    )
    sensorInventory: dict = field(
        default_factory=dict
    )

    def __post_init__(self):
        
        super().__post_init__()

@dataclass(kw_only=True)
class CR1000x(logger):
    model: str = 'CR1000x'
    manufacturer: str = 'CSI'

callMeasurement()

# supportedLoggers = ['CR1000','CR1000x','Smart-Flux','Hobo']

# @dataclass(kw_only=True)
# class dataLogger(baseClass):
#     def __post_init__(self):
#         super().__post_init__()

# @dataclass
# class CR1000(dataLogger):