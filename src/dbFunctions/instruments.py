import os
# from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict

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
}

@dataclass(kw_only=True)
class instrument(baseFunctions):
    n: int = field(default=1,repr=False)
    instrumentType: str = field(
        default='sonic',
        repr=False,
        metadata={
            'description': 'Indicates type of instrument (see options)',
            'options':['sonic','irga','met']
            })
    manufacturer: str = None
    model: str = field(
        default=None,
        metadata={
            'description': 'Indicates the instrument model (see options)',
            'options':list(supportedInstruments.keys())
            })
    serialNumber: str = None
    softwareVersion: str = None
    instrumentID: str = None
    measurementHeight: float = field(default = 0.0,metadata={'req':['sonic']})
    northOffset: float = field(default = 0.0,metadata={'req':['sonic']})
    windFormat: str = field(default = 'uvw',metadata={'req':['sonic']})
    tubeLength: float = field(default = 0.0, metadata={'req':['irga']})
    tubeDiameter: float = field(default = 0.0, metadata={'req':['irga']})
    tubeFlowRate: float = field(default = 0.0, metadata={'req':['irga']})
    northwardSeparation: float = 0.0
    eastwardSeparation: float = 0.0
    verticalSeparation: float = 0.0

    def __post_init__(self):
        for key,value in self.__dataclass_fields__.items():
            if 'req' in value.metadata:
                if self.instrumentType in value.metadata['req']:
                    self.__dataclass_fields__[key].repr = True
                else:
                    self.__dataclass_fields__[key].repr = False
        if self.model is not None:
            self.manufacturer = supportedInstruments[self.model]


@dataclass(kw_only=True)
class instrumentSet(baseFunctions):
    version: str = field(default='v1.0',repr=False)
    instruments: list = field(default_factory=lambda:[
        instrument(),
        instrument(instrumentType='irga'),
        instrument(instrumentType='irga'),
        instrument(instrumentType='met')
    ],repr=False)
    startDate: datetime = None
    configuration: dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        # self.startDate = self.startDate.strftime('%Y-%m-%dT%H:%M:%SZ')
        for i,instr in enumerate(self.instruments):
            instr.n = i+1
            instr.__post_init__()
            self.configuration['instr_'+str(instr.n)] = dcToDict(instr,repr=True,inheritance=False)