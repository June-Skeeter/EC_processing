from dataclasses import dataclass, field, MISSING
from ..helperFunctions.baseFunctions import baseFunctions

@dataclass(kw_only=True)
class testSensor(baseFunctions):
    UID: str = None
    model: str = 'test'