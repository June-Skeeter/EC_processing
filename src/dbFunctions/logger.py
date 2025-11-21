# import os
# from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict


default_comment = f'''
Measurement configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''



supportedLoggers = ['CR1000','CR1000x','Smart-Flux','Hobo']

@dataclass(kw_only=True)
class dataLogger(baseFunctions):
    loggerID: str = None
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
            'description': 'Only provide if different from site-coordinates'
    })
    longitude: str = field(
        metadata = {
            'description': 'Only provide if different from site-coordinates'
    })
    programHistory: dict = field(
        default_factory=dict,
    )
    sensorInventory: dict = field(
        default_factory=dict
    )

    def __post_init__(self):
        super().__post_init__()

@dataclass
class CR1000(dataLogger):