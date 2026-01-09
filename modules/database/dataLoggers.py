from dataclasses import dataclass, field
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class dataLogger(baseClass):
    loggerModel: str = field(
        init=False,
        metadata = {
            'description': 'The logger model, auto-filled from class name',
    })
    stationName: str = field(
        default = '',
        metadata = {
            'description': 'Custom descriptor variable',
    })
    manufacturer: str = field(
        default = '',
        metadata = {
            'description': 'Self explanatory',
    })
    serialNumber: str = field(
        default = '',
        metadata = {
            'description': 'Serial# (if known)',
    })
    fileType: str = field(
        default=None,
        metadata={'description':'Type of file associated with the logger/system',
                  'options':['dat','ghg','csv']}
    )

    def __post_init__(self):
        self.loggerModel = type(self).__name__

@dataclass(kw_only=True)
class CR1000X(dataLogger):
    manufacturer: str = 'CSI'
    fileType: str = 'dat'

@dataclass(kw_only=True)
class CR1000(dataLogger):
    manufacturer: str = 'CSI'
    fileType: str = 'dat'

@dataclass
class HOBO(dataLogger):
    manufacturer: str = 'onset'
    fileType: str = 'csv'

@dataclass
class LI7550(dataLogger):
    manufacturer: str = 'LICOR'
    fileType: str = 'ghg'