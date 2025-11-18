import os
# from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict
from .project import project



default_comment = f'''
Instrument inventory file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

# Instrument: Manufacturer
supportedInstruments = {
    #Sonics & IRGAs
    'IRGASON':'CSI',
    'CSAT3':'CSI',
    'CSAT3B':'CSI',
    'LI7700':'LICOR',
    'LI7200':'LICOR',
    'LI7500':'LICOR',
    'LI7500A':'LICOR',
    #Met instruments
    'HMP35A':'Vaisala',
    'example':None
}


@dataclass(kw_only=True)
class instrument(baseFunctions):
    instrumentType: str = field(
        default=None,
        metadata={
            'description': 'The type of instrument',
            'options':['sonic','irga','generic']
            })
    manufacturer: str = field(
        default=None,
        metadata={
            'description': 'Indicates manufacturer of instrument, auto-filled from instrument model',
            })
    model: str = field(
        metadata={
            'description': 'The instrument model (see supportedInstruments)',
            'options':list(supportedInstruments.keys())
            })
    serialNumber: str = field(
        default=None,
        metadata={
            'description': 'Serial no (if known)',
            })
    softwareVersion: str =  field(
        default=None,
        metadata={
            'description': 'Software version (if known/exists)',
            })
    # measurementHeight: float = field(
    #     metadata={
    #         'required':['sonic'],
    #         'description': 'Measurement height (Zm) in meters, required for Sonics, optional otherwise',
    #         })
    # northOffset: float = field(
    #     metadata={
    #         'required':['sonic'],
    #         'description': 'Offset from North in degrees (clockwise)',
    #         })
    # windFormat: str = field(
    #     default=None,
    #     metadata={
    #         'description': 'Format of wind data (only supports uvw for now).  Required for EddyPro',
    #         'required':['sonic'],
    #         'options':['uvw']
    #         })
    # tubeLength: float = field(
    #     metadata={
    #         'description':'Lenght of intake tube (only for irga-closed)',
    #         'required':['irga-closed']
    #         })
    # tubeDiameter: float = field(
    #     metadata={
    #         'description':'Lenght of intake tube (only for irga-closed)',
    #         'required':['irga-closed']
    #         })
    # tubeFlowRate: float = field(
    #     metadata={
    #         'description':'Lenght of intake tube (only for irga-closed)',
    #         'required':['irga-closed']
    #         })
    # northwardSeparation: float = field(
    #     metadata={
    #         'description':'Northward separation from reference sonic (in cm) only required for irga-open, irga-closed, and any secondary sonics.  Optional for other sensors.',
    #         'required':['irga-closed','irga-open']
    #         })
    # eastwardSeparation: float = field(
    #     metadata={
    #         'description':'Northward separation from reference sonic (in cm) only required for irga-open, irga-closed, and any secondary sonics.  Optional for other sensors.',
    #         'required':['irga-closed','irga-open']
    #         })
    # verticalSeparation: float = field(
    #     metadata={
    #         'description':'Northward separation from reference sonic (in cm) only required for irga-open, irga-closed, and any secondary sonics.  Optional for other sensors.',
    #         'required':['irga-closed','irga-open']
    #         })

    def __post_init__(self):
        # if self.model is None:
        #     self.logWarning('No instrument provided, generating generic template')
        #     for key,value in self.__dataclass_fields__.items():
        #         val = 'Variable is a '+value.type.__name__+' type. '
        #         if 'description' in value.metadata:
        #             val = val + value.metadata['description']
        #         if 'options' in value.metadata:
        #             val = val +'. Must be one of [' +', '.join(value.metadata['options'])+']'

        #         self.__dict__[key] = val
        # else:
        #     for key,value in self.__dataclass_fields__.items():
        #         if 'required' in value.metadata:
        #             if self.instrumentType in value.metadata['required']:
        #                 self.__dataclass_fields__[key].repr = True
        #             elif value is None:
        #                 self.__dataclass_fields__[key].repr = False
        # self.manufacturer = supportedInstruments[self.model]
        super().__post_init__()

@dataclass(kw_only=True)
class sonic(instrument):
    instrumentType: str = 'soinc'
    windFormat: str
    measurementHeight: float
    northOffset: float
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0
    
    def __post_init__(self):
        super().__post_init__()

@dataclass(kw_only=True)
class IRGASON_sonic(sonic):
    model: str = 'IRGASON'
    windFormat: str = 'uvw'
    manufacturer: str = 'CSI'

    def __post_init__(self):
        super().__post_init__()

@dataclass(kw_only=True)
class irga_open(instrument):
    instrumentType: str = 'irga'
    northwardSeparation: float
    eastwardSeparation: float
    verticalSeparation: float
    
    def __post_init__(self):
        super().__post_init__()

@dataclass(kw_only=True)
class IRGASON_irga(irga_open):
    model: str = 'IRGASON'
    manufacturer: str = 'CSI'
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0

    def __post_init__(self):
        super().__post_init__()

@dataclass(kw_only=True)
class LI7700(irga_open):
    model: str = 'LI7700'
    manufacturer: str = 'LICOR'

# class irga_closed(instrument):
    # instrumentType: str = 'irga'
#     t



# IRGASON_sonic()# = instrument(model='IRGASON',instrumentType='sonic')
# IRGASON_irga = instrument(model='IRGASON',instrumentType='irga')
# print(i)