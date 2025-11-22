from typing import Iterable
from dataclasses import dataclass, field, MISSING
from ..helperFunctions.baseFunctions import baseFunctions

@dataclass(kw_only=True)
class testLogger:
    model: str = field(init=False)
    manufacturer: str =  field(default=None,init=False)
    sensorInventory: Iterable = field(default_factory=dict)

    def __post_init__(self):
        self.__pre_init__(False)

    def __pre_init__(self,proceed=True):
        self.model = type(self).__name__