import numpy as np
from typing import Iterable
from dataclasses import dataclass, field
from modules.databaseSetup.spatialObject import spatialObject

# dataclasses to define specs/default values for sensors

@dataclass(kw_only=True)
class sensor(spatialObject):
    verbose: bool = field(default=False,repr=False)
    sensorModel: str = field(init=False,default=None)
    sensorID: str = field(default=None,metadata = {'description': 'The sensor model, auto-filled from class name',})
    manufacturer: str = field(default = '',metadata = {'description': 'Indicates manufacturer of sensor, auto from class name',})
    serialNumber: str = field(default = '',metadata = {'description': 'Serial# (if known)',})
    sensorType: str = field(default='',repr=False)
    traceMetadataMap: dict = field(default=None)
    UID_name = 'sensorID'
    UID_source = 'sensorModel'

    def __post_init__(self):
        self.sensorModel = type(self).__name__
        if self.sensorID is None:
            self.sensorID = self.sensorModel
        elif self.sensorID is None:
            self.logError('Provide sensor ID for generic instrumentation')
        super().__post_init__()

# BIOMET sensors
@dataclass(kw_only=True)
class thermocouple(sensor):
    sensorType: str = 'thermocouple'

@dataclass(kw_only=True)
class SN500(sensor):
    manufacturer: str = 'Apogee'
    sensorType: str = 'net-radiometer'

@dataclass(kw_only=True)
class HMP(sensor):
    manufacturer: str = 'Vaisala'
    sensorType: str = 'temperature-humidity'

@dataclass(kw_only=True)
class voltage(sensor):
    pass

## Eddy Covariance Sensors require enhanced functionality because of their positional relationship to on-another

@dataclass(kw_only=True)
class ecSensor(sensor):
    measurementHeight: float = field(default = None, metadata = {'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise'})
    northOffset: float = field(default = None, metadata = {'description': 'Offset from North in degrees (clockwise) of main sonic'})
    northwardSeparation: float = field(default = None,metadata = {'description':'Northward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.'})
    eastwardSeparation: float = field(default = None,metadata = {'description':'Eastward separation from reference sonic (in m) required for irgas, and any secondary sonics.  Calculated from x&y separation if not provided.'})
    verticalSeparation: float = field(default = None,metadata = {'description':'Vertical separation from reference sonic (in m) required for irgas, and any secondary sonics.'})
    xSeparation: float = field(default = None,metadata = {'description':'Lateral separation from reference sonic (in m) parallel to the main axis of the sonic (towards mast/sonic head = positive).  See Fig D2 in (https://s.campbellsci.com/documents/us/manuals/easyflux-dl-cr6op.pdf) for example.  Required for irgas, and any secondary sonics to calculate northward/eastward separation if not provided.',})
    ySeparation: float = field(default = None,metadata = {'description':'Lateral separation from reference sonic (in m) perpendicular to the main axis of the sonic (right of mast/sonic head = positive).  See Fig D2 in (https://s.campbellsci.com/documents/us/manuals/easyflux-dl-cr6op.pdf) for example.  Required for irgas, and any secondary sonics to calculate northward/eastward separation if not provided.',})
    zSeparation: float = field(default = None,repr = False,metadata = {'description':'Synonymous with Vertical separation from reference sonic (in m) required for irgas, and any secondary sonics.',})
    windFormat: str = field(default=None,metadata = {'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro','options':['uvw']})


    def __post_init__(self):
        super().__post_init__()
        # x,y,z are alternative formats
        # z & vertical are synonymous so always drop z
        if self.verticalSeparation == None and self.zSeparation is not None:
            self.verticalSeparation = self.zSeparation
        self.zSeparation = None

@dataclass(kw_only=True)
class IRGASON(ecSensor):
    manufacturer: str = 'Campbell Scientific'
    sensorType: str = 'sonic-irga-open-path'
    measurementHeight: float
    northOffset: float
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
    windFormat: str = 'uvw'
    defaultTraceMap: dict = field(
        repr=False,
        default_factory=lambda:{
            'Ux':{'measurementType':''},
            'Uy':{'measurementType':''},
            'Uz':{'measurementType':''},
            'T_SONIC':{'measurementType':''},
            'diag_sonic':{'measurementType':''},
            'CO2_density':{'measurementType':'molar_density'},
            'CO2_density_fast_tmpr':{'measurementType':''},
            'H2O_density':{'measurementType':'molar_density'},
            'diag_irga':{'measurementType':''},
            'T_SONIC_corr':{'measurementType':''},
            'PA':{'measurementType':''},
            'CO2_sig_strgth':{'measurementType':''},
            'H2O_sig_strgth':{'measurementType':''},
        })

    def __post_init__(self):
        super().__post_init__()
    
@dataclass(kw_only=True)
class CSAT3(ecSensor):
    manufacturer: str = 'Campbell Scientific'
    sensorType: str = 'sonic'
    measurementHeight: float
    northOffset: float
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
    windFormat: str = 'uvw'
    

@dataclass(kw_only=True)
class LI7700(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-open-path'

@dataclass(kw_only=True)
class LI7500(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-open-path'

@dataclass(kw_only=True)
class LI7200(ecSensor):
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-closed-path'
    tubeLength: float = field(default=5.33,metadata = {'description':'Length of intake tube (only for closed path irgas)',})
    tubeDiameter: float = field(metadata = {'description':'Diameter of intake tube (only for closed path irgas)',})

@dataclass(kw_only=True)
class fwThermocouple(ecSensor):
    sensorType: str = 'thermocouple'

@dataclass(kw_only=True)
class CSI_T107(ecSensor):
    manufacturer: str = 'Campbell Scientific'
    sensorType: str = 'thermistor'
    defaultTraceMap: Iterable = field(
        repr=False,
        default_factory=lambda:{
        'TA_1_1_1':{'measurementType': 'temperature'}
    })
    # These values aren't needed for any flux calculations either
    northwardSeparation: float = None
    eastwardSeparation: float = None
    verticalSeparation: float = None
