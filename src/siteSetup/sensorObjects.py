from dataclasses import dataclass, field, MISSING
from src.siteSetup.defaultObject import defaultObject

@dataclass(kw_only=True)
class genericSensor(defaultObject):
    model: str = field(
        init=False,
        metadata = {
            'description': 'The sensor model, auto-filled from class name',
    })
    manufacturer: str = field(
        default = None,
        init=False,
        metadata = {
            'description': 'Indicates manufacturer of sensor, auto from class name',
    })
    serialNumber: str = field(
        default = None,
        metadata = {
            'description': 'Serial# (if known)',
    })
    sensorType: str = field(
        default='general',
        metadata = {
            'description': 'The type of sensor',
            'options':['flux','general']
    })
    
    def __post_init__(self):
        self.model = type(self).__name__
        self.UID = self.model


######################################## Flux Sensors ########################################

# Below are parameters required by EddyPro for processing of high frequency data
# Some are specific to Sonics or IRGAs, some are common to all

@dataclass(kw_only=True)
class fluxSensor(genericSensor):
    sensorType: str = 'flux'
    softwareVersion: str =  field(
        default = None,
        metadata = {
            'description': 'Software version (if known/exists)',
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
@dataclass(kw_only=True)
class sonicAnemometer(fluxSensor):
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
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


@dataclass(kw_only=True)
class IRGASON_sonic(sonicAnemometer):
    manufacturer: str = 'CSI'

@dataclass(kw_only=True)
class CSAT3(sonicAnemometer):
    manufacturer: str = 'CSI'

class infraredGasAnalyzer(fluxSensor):
    tubeLength: float = field(
        default = '',
        metadata = {
            'description':'Length of intake tube (only for closed path irgas)',
    })
    tubeDiameter: float = field(
        default = '',
        metadata = {
            'description':'Diameter of intake tube (only for closed path irgas)',
    })

@dataclass(kw_only=True)
class IRGASON_irga(infraredGasAnalyzer):
    manufacturer: str = 'CSI'
    tubeLength: float = 0.0
    tubeDiameter: float = 0.0
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0

@dataclass(kw_only=True)
class LI7700(infraredGasAnalyzer):
    manufacturer: str = 'LICOR'
    tubeLength: float = 0.0
    tubeDiameter: float = 0.0

@dataclass(kw_only=True)
class LI7500(infraredGasAnalyzer):
    manufacturer: str = 'LICOR'
    tubeLength: float = 0.0
    tubeDiameter: float = 0.0

@dataclass(kw_only=True)
class LI7200(infraredGasAnalyzer):
    manufacturer: str = 'LICOR'
    tubeDiameter: float = 5.33