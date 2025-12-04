from dataclasses import dataclass, field
# from src.helperFunctions.baseClass import baseClass
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class rawTraceIn(baseClass):
    variableNumber: int = field(default=1,repr=False) # Counter variable to represent position (in source file or processing order)
    variableName: str
    units: str = None
    dtype: str = None
    ignore: bool = False
    minMax: list = field(default_factory=list)
    sensorID: str = None

    def __post_init__(self):
        return super().__post_init__()