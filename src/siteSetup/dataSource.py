from typing import Iterable
from dataclasses import dataclass, field, MISSING

from ..helperFunctions.getClasses import getClasses

from src.siteSetup.defaultObject import defaultObject

# Get all defined sensors
import src.siteSetup.sensorObjects as sensorObjects
sensorObjects = getClasses(sensorObjects)
sensorObjects = {cl.__name__:cl for cl in sensorObjects[::-1]}

@dataclass(kw_only=True)
class genericSource(defaultObject):
    sourceType: str = field(
        init = False,
        metadata={
            'description':'Type of data source',
        }
    )
    fileType: str = field(
        metadata={
            'description': 'type of file associated with the input data source',
        }
    )
    sourceFiles: dict = field(
        default_factory=dict,
        init=False,
        repr=False
    )
    # traces: dict = field(
    #     default_factory=dict,
    #     metadata={
    #         'description': 'Dictionary linking traces to sensors/instrumentation',
    #     }
    # )

    def __post_init__(self):
        if not hasattr(self,'UID'):
            self.UID = type(self).__name__
            self.sourceType = None
        super().__post_init__()

@dataclass(kw_only=True)
class manualMeasurement(genericSource):
    sourceType: str = 'manualMeasurement'
    description: str = None
    fileType: str = 'csv'

@dataclass(kw_only=True)
class externalMeasurement(genericSource):
    sourceType: str = 'externalMeasurement'
    description: str = None
    fileType: str = 'csv'

    
@dataclass(kw_only=True)
class dataLogger(genericSource):
    sourceType: str = 'dataLogger'
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
    sensorInventory: Iterable = field(
        default_factory=lambda:[sensorObjects['genericSensor']()],
        metadata={
            'description':'Inventory of sensors linked to the logger',
            'options':{name:value.template() for name,value in sensorObjects.items()}
            })

    def __post_init__(self):
        self.model = type(self).__name__
        self.UID = self.model
        self.nestedClasses = sensorObjects
        self.sensorInventory = self.parseNestedObjects(
            objectsToParse = self.sensorInventory,
            objectOptions = sensorObjects,
            objectID = 'model')
        super().__post_init__()

@dataclass(kw_only=True)
class CR1000x(dataLogger):
    manufacturer: str = 'CSI'
    fileType: str = 'TOB3'

@dataclass
class HOBO(dataLogger):
    manufacturer: str = 'Onset'
    fileType: str = 'csv'