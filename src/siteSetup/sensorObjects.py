from dataclasses import dataclass, field, MISSING
from src.databaseObjects.defaultObjects import spatialObject

@dataclass(kw_only=True)
class genericSensor(spatialObject):
    sensorID: str = field(default=None,init=False)
    sensorModel: str = field(
        init=False,
        metadata = {
            'description': 'The sensor model, auto-filled from class name',
    })
    name: str = field(
        default = None,
        metadata = {
            'description': 'Custom descriptor variable',
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
    measurementType: str = field(
        default='general',
        metadata = {
            'description': 'The type of measurement obtained by the sensor'
    })
    
    def __post_init__(self):
        self.sensorModel = type(self).__name__
        if self.serialNumber:
            self.sensorID = f"{self.sensorModel}_{self.serialNumber}"
        elif self.name:
            self.sensorID = f"{self.sensorModel}_{self.name.replace(' ','_')}"
        else:
            self.sensorID = f"{self.sensorModel}_{self.index}"
        super().__post_init__()

@dataclass(kw_only=True)
class thermocouple(genericSensor):
    pass


######################################## Flux Sensors ########################################

# Below are parameters required by EddyPro for processing of high frequency data
# Some are specific to Sonics or IRGAs, some are common to all

@dataclass(kw_only=True)
class ecSystem(spatialObject):
    measurementType: str = 'flux'
    softwareVersion: str =  field(
        default = None,
        metadata = {
            'description': 'Software version (if known/exists)',
    })
    northwardSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.',
    })
    eastwardSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.',
    })
    verticalSeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.',
    })

    xSeparation: float = field(
        metadata = {
            'description':'Lateral separation from reference sonic (in m) parallel to the main axis of the sonic.  See Fig D2 in (https://s.campbellsci.com/documents/us/manuals/easyflux-dl-cr6op.pdf) for example.  Required for irgas, and any secondary sonics.',
    })
    ySeparation: float = field(
        metadata = {
            'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.',
    })


# @dataclass(kw_only=True)
# class sonicAnemometer(fluxSensor):
#     northwardSeparation: float = 0.0
#     eastwardSeparation: float = 0.0
#     verticalSeparation: float = 0.0
#     windFormat: str = field(
#         default='uvw',
#         metadata = {
#             'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro',
#             'options':['uvw']
#     })
#     measurementHeight: float = field(
#         metadata = {
#             'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise',
#     })
#     northOffset: float = field(
#         metadata = {
#             'description': 'Offset from North in degrees (clockwise)',
#     })


# @dataclass(kw_only=True)
# class IRGASON_sonic(sonicAnemometer):
#     manufacturer: str = 'CSI'

# @dataclass(kw_only=True)
# class CSAT3(sonicAnemometer):
#     manufacturer: str = 'CSI'

# @dataclass
# class infraredGasAnalyzer(fluxSensor):
#     tubeLength: float = field(
#         default = 0.0,
#         metadata = {
#             'description':'Length of intake tube (only for closed path irgas)',
#     })
#     tubeDiameter: float = field(
#         default = 0.0,
#         metadata = {
#             'description':'Diameter of intake tube (only for closed path irgas)',
#     })

# @dataclass(kw_only=True)
# class IRGASON_irga(infraredGasAnalyzer):
#     manufacturer: str = 'CSI'
#     tubeLength: float = 0.0
#     tubeDiameter: float = 0.0
#     northwardSeparation: float = 0.0
#     eastwardSeparation: float = 0.0
#     verticalSeparation: float = 0.0

# @dataclass(kw_only=True)
# class LI7700(infraredGasAnalyzer):
#     manufacturer: str = 'LICOR'
#     tubeLength: float = 0.0
#     tubeDiameter: float = 0.0

# @dataclass(kw_only=True)
# class LI7500(infraredGasAnalyzer):
#     manufacturer: str = 'LICOR'
#     tubeLength: float = 0.0
#     tubeDiameter: float = 0.0

# @dataclass(kw_only=True)
# class LI7200(infraredGasAnalyzer):
#     manufacturer: str = 'LICOR'
#     tubeDiameter: float = 5.33