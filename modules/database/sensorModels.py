import numpy as np
import inspect
import sys
from typing import Iterable
from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass
from modules.database.spatialObjects import pointObject

# dataclasses to define specs/default values for sensors

@dataclass(kw_only=True)
class sensor(pointObject,baseClass):
    verbose: bool = field(default=False,repr=False)
    sensorModel: str = field(init=False,default=None)
    sensorID: str = field(default=None,metadata = {'description': 'The sensor model, auto-filled from class name',})
    manufacturer: str = field(default = '',metadata = {'description': 'Indicates manufacturer of sensor, auto from class name',})
    serialNumber: str = field(default = '',metadata = {'description': 'Serial# (if known)',})
    sensorType: str = field(default='',repr=False)
    measurementHeight: float = field(default = None, metadata = {'description': 'Measurement height (Zm) optional for BIOMET sensors'})
    traceMetadata: dict = field(default=None)

    def __post_init__(self):
        # if self.sensorModel is None:
        #     self.sensorModel = type(self).__name__
        self.formatUID('sensorModel')
        if self.sensorID is None:
            self.sensorID = self.UID
        elif self.sensorID is None:
            self.logError('Provide sensor ID for generic instrumentation')
        super().__post_init__()

# BIOMET sensors
@dataclass(kw_only=True)
class thermocouple(sensor):
    sensorModel: str = 'thermocouple'
    sensorType: str = 'thermocouple'

@dataclass(kw_only=True)
class NRLite(sensor):
    sensorModel: str = 'NRLite'
    manufacturer: str = 'Kipp & Zonen'
    sensorType: str = 'net-radiometer'

@dataclass(kw_only=True)
class SN500(sensor):
    sensorModel: str = 'SN500'
    manufacturer: str = 'Apogee'
    sensorType: str = 'net-radiometer'

@dataclass(kw_only=True)
class HMP155(sensor):
    sensorModel: str = 'HMP'
    manufacturer: str = 'Vaisala'
    sensorType: str = 'temperature-humidity'

@dataclass(kw_only=True)
class BaroVue(sensor):
    sensorModel: str = 'BaroVue'
    manufacturer: str = 'CSI'
    sensorType: str = 'Barometer'

@dataclass(kw_only=True)
class PLS(sensor):
    sensorModel: str = 'PLS'
    manufacturer: str = 'OTT'
    sensorType: str = 'Pressure Transducer'

@dataclass(kw_only=True)
class VoltDiff(sensor):
    sensorModel: str = 'VoltDiff'
    sensorType: str = 'dataLogger'


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
    windFormat: str = field(default=None,metadata = {'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro','options':['uvw', 'polar_w', 'axis']})


    def __post_init__(self):
        super().__post_init__()
        # x,y,z are alternative formats
        # z & vertical are synonymous so always drop z
        if self.verticalSeparation == None and self.zSeparation is not None:
            self.verticalSeparation = self.zSeparation
        self.zSeparation = None

@dataclass(kw_only=True)
class IRGASON(ecSensor):
    sensorModel: str = 'IRGASON'
    manufacturer: str = 'CSI'
    sensorType: str = 'sonic-irga-open-path'
    measurementHeight: float
    northOffset: float
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
    windFormat: str = 'uvw'

    def __post_init__(self):
        super().__post_init__()
    
@dataclass(kw_only=True)
class CSAT3(ecSensor):
    sensorModel: str = 'CSAT3'
    manufacturer: str = 'CSI'
    sensorType: str = 'sonic'
    measurementHeight: float
    northOffset: float
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
    windFormat: str = 'uvw'

@dataclass(kw_only=True)
class LI7700(ecSensor):
    sensorModel: str = 'LI7700'
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-open-path'

@dataclass(kw_only=True)
class LI7500(ecSensor):
    sensorModel: str = 'LI7500'
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-open-path'

@dataclass(kw_only=True)
class LI7200(ecSensor):
    sensorModel: str = 'LI7200'
    manufacturer: str = 'LICOR'
    sensorType: str = 'irga-closed-path'
    tubeLength: float = field(default=5.33,metadata = {'description':'Length of intake tube (only for closed path irgas)',})
    tubeDiameter: float = field(metadata = {'description':'Diameter of intake tube (only for closed path irgas)',})

@dataclass(kw_only=True)
class fwThermocouple(ecSensor):
    # sensorModel: str = 'LI7200'
    sensorType: str = 'thermocouple'

@dataclass(kw_only=True)
class CSI_T107(ecSensor):
    sensorModel: str = 'CSI_T107'
    manufacturer: str = 'CSI'
    sensorType: str = 'thermistor'
    # These values aren't needed for any flux calculations either
    northwardSeparation: float = None
    eastwardSeparation: float = None
    verticalSeparation: float = None



# Function to get classes in the current script
def get_classes_in_current_script():
    current_module = sys.modules[__name__]
    classes = []
    
    # Use inspect.getmembers with inspect.isclass predicate
    for name, obj in inspect.getmembers(current_module, inspect.isclass):
        # Additional check to ensure the class is defined in the current module 
        # and not just imported (e.g., the `inspect` module's own classes)
        if obj.__module__ == current_module.__name__:
            classes.append(obj)
            
    return classes

# Get the list of classes
sensorObjects = get_classes_in_current_script()
sensorModels = {s.sensorModel:s for s in sensorObjects}


