from dataclasses import dataclass, field
# from src.helperFunctions.baseClass import baseClass
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class rawTraceIn(baseClass):
    variableNumber: int = field(default=1,repr=False) # Counter variable to represent position (in source file or processing order)
    variableNameIn: str
    variableNameOut: str = None
    units: str = ''
    dtype: str = None
    ignore: bool = False
    operation: str = None
    measurementType: str = ''
    minMax: list = field(default_factory=lambda:[None,None])
    sensorID: str = ''
    traceMetadataMap: dict = field(default_factory=dict,repr=False)
    ignoreByDefault: list = field(default_factory=list,repr=False)
    verbose: str = None

    def __post_init__(self):
        if self.variableNameIn in self.traceMetadataMap:
            for key,value in self.traceMetadataMap[self.variableNameIn].items():
                setattr(self,key,value)
        if self.variableNameIn in self.ignoreByDefault:
            self.ignore = True
        return super().__post_init__()