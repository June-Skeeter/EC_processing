import os
import inspect
import sys
# from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict
from .project import project


supportedSensors = [
    'genericSensor',
    'genericIrga',
    'genericSonic',
    'CSAT3',
    'IRGASON_sonic',
    'IRGASON_irga',
    'LI7200',
    'LI7500',
    'LI7700'
    ]

# Generic parameters common to all sensors
@dataclass(kw_only=True)
class genericSensor(baseFunctions):
    preserveInheritedMetadata: bool = field(default=True,repr=False)
    sensorID: str = field(
        default = None,
        metadata = {
            'description': 'Indicates manufacturer of sensor, auto-filled from sensor model + a unique ID if duplicates',
    })
    sensorType: str = field(
        default='general',
        metadata = {
            'description': 'The type of sensor',
            'options':['sonic','irga','general']
    })
    manufacturer: str = field(
        default = None,
        metadata = {
            'description': 'Indicates manufacturer of sensor',
    })
    model: str = field(
        default = None,
        metadata = {
            'description': 'The sensor model',
            'options':supportedSensors
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
        default = None,
        metadata = {
            'description': 'Only provide if different from site-coordinates'
    })
    # comments: str = None

    def __post_init__(self):
        self.model = type(self).__name__
        self.UID()
        super().__post_init__()
    
    def UID(self,i=1):
        self.sensorID = f"{type(self).__name__}_{i}"

################# Sonic Anemometers #################

# Specific generic sub-types of sensors (these must be associated with a specific model)
@dataclass(kw_only=True)
class genericSonic(genericSensor):
    # Parameters for all sonic types
    sensorType: str = 'sonic'
    softwareVersion: str =  field(
        default = None,
        metadata = {
            'description': 'Software version (if known/exists)',
    })
    windFormat: str = field(
        default='uvw',
        metadata = {
            'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro',
            'options':['uvw']
    })
    measurementHeight: float = field(
        metadata = {
            'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise',
    })
    northOffset: float = field(
        metadata = {
            'description': 'Offset from North in degrees (clockwise)',
    })
    northwardSeparation: float = field(
        default = 0.0,
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    eastwardSeparation: float = field(
        default = 0.0,
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    verticalSeparation: float = field(
        default = 0.0,
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    
    def __post_init__(self):
        super().__post_init__()
        
@dataclass(kw_only=True)
class CSAT3(genericSonic):
    manufacturer: str = 'CSI'

@dataclass(kw_only=True)
class IRGASON_sonic(genericSonic):
    manufacturer: str = 'CSI'
    
################# Infrared Gas Analyzers #################

@dataclass(kw_only=True)
class genericIrga(genericSensor):
    # Parameters for all irga types
    sensorType: str = 'irga'
    closedPath: bool = field(
        metadata = {
            'description':'True if irga is closed path'
    })
    northwardSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    eastwardSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    verticalSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in cm) required for irgas, and any secondary sonics.',
    })
    tubeLength: float = field(
        metadata = {
            'description':'Lenght of intake tube (only for irgas-closed)',
    })
    tubeDiameter: float = field(
        metadata = {
            'description':'Lenght of intake tube (only for irgas-closed)',
    })

@dataclass(kw_only=True)
class openIrga(genericIrga):
    closedPath: bool = False
    tubeLength: float = 0.0
    tubeDiameter: float = 0.0
    
@dataclass(kw_only=True)
class closedIrga(genericIrga):
    closedPath: bool = True

@dataclass(kw_only=True)
class IRGASON_irga(openIrga):
    manufacturer: str = 'CSI'
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0

@dataclass(kw_only=True)
class LI7700(openIrga):
    manufacturer: str = 'CSI'

@dataclass(kw_only=True)
class LI7500(openIrga):
    manufacturer: str = 'CSI'

@dataclass(kw_only=True)
class LI7200(closedIrga):
    manufacturer: str = 'CSI'



#################

def callSensor(UID):
    allSensors = {s:eval(s) for s in supportedSensors}
    ID = UID.rsplit('_',1)[0]
    return(allSensors[ID])