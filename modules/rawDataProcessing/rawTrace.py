from dataclasses import dataclass, field
# from src.helperFunctions.baseClass import baseClass
from modules.database.dbTrace import trace

@dataclass(kw_only=True)
class rawTraceIn(trace):
    variableNumber: int = field(default=1,repr=False) # Counter variable to represent position (in source file or processing order)
    originalVariable: str
    dateRange: list = field(default_factory=list)
    # variableName: str
    # variableNameOut: str = None
    # units: str = ''
    # dtype: str = None
    # ignore: bool = False
    operation: str = None
    measurementType: str = ''
    minMax: list = field(default_factory=list)
    sensorID: str = ''
    traceMetadata: dict = field(default_factory=dict,repr=False)
    ignoreByDefault: list = field(default_factory=list,repr=False)
    # verbose: str = None

    def __post_init__(self):
        if self.variableName == self.__dataclass_fields__['variableName'].default:
            self.variableName = self.originalVariable
        # breakpoint()
        if self.traceMetadata is not None and self.variableName in self.traceMetadata:
            for key,value in self.traceMetadata[self.variableName].items():
                setattr(self,key,value)
        if self.variableName in self.ignoreByDefault:
            self.ignore = True
        if self.units == '%':
            self.units = 'percent'
        return super().__post_init__()