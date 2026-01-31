import fnmatch
from dataclasses import dataclass, field
from submodules.helperFunctions.baseClass import baseClass
from submodules.helperFunctions.safeFormat import safeFormat,cleanString


@dataclass(kw_only=True)
class trace(baseClass):
    variableName: str = field(default='', metadata={'description':'defaults to inputFileName, change to output as a different filename'})
    title: str = field(default='', metadata={'description':'long-form title'})
    units: str = field(default='', metadata={'description':''})
    dtype: str = field(default='float32',metadata={'description':'data type (float, string, etc.)'})
    ignore: bool = False


@dataclass(kw_only=True)
class rawTrace(trace):
    # variableNumber: int = field(default=1,repr=False) # Counter variable to represent position (in source file or processing order)
    originalVariable: str
    fileName: str = None
    dateRange: list = field(default_factory=list)
    operation: str = None
    measurementType: str = ''
    minMax: list = field(default_factory=list)
    sensorID: str = ''
    traceMetadata: dict = field(default_factory=dict,repr=False)
    ignoreByDefault: list = field(default_factory=list,repr=False)
    partialMatch: bool = field(default=False,repr=False)

    def __post_init__(self):
        self.originalVariable = cleanString(self.originalVariable)
        if self.variableName == self.__dataclass_fields__['variableName'].default:
            self.variableName = safeFormat(self.originalVariable)
        if self.fileName == self.__dataclass_fields__['fileName'].default:
            self.fileName = safeFormat(self.originalVariable)

        if self.traceMetadata is not None:
            if self.partialMatch:
                m = [k for k in self.traceMetadata if fnmatch.fnmatch(self.originalVariable,k)]
                if len(m)>1:
                    self.logError('Multi-match, give more precise fnmatch wildcard')
                elif len(m)==1:
                    self.traceMetadata[self.originalVariable] = self.traceMetadata[m[0]]
            if self.originalVariable in self.traceMetadata:
                for key,value in self.traceMetadata[self.originalVariable].items():
                    setattr(self,key,value)
        if self.originalVariable in self.ignoreByDefault:
            self.ignore = True
        if self.units == '%':
            self.units = 'percent'
        super().__post_init__()
    

@dataclass(kw_only=True)
class firstStageTrace(trace):
    inputFileName: list = field(metadata={'description':'name of the raw input file'})
    inputFileName_dates: list = field(metadata={'description':'date rang corresponding to input FileName (s)'})
    instrumentType: str = field(default='', metadata={'description':''})
    measurementType: str = field(metadata={'description':'taken from measurementType variable'})
    minMax: list = field(default_factory=list, metadata={'description':'optional to set min/max clipping'})
    zeroPt: list = field(default_factory=lambda:[-9999], metadata={'description':'default NaN value (not actually zero)'})
    Evaluate: str = field(default='',metadata={'description':'Code block, evaluated using an exec statement, to manipulate the trace variable'})
    originalVariable: str = field(default='',metadata={'description':'Name of the variable as given in the source file'})
    
    # Required for second stage
#     variableName: str = None
#     title: str = ''
#     units: str = ''
#     inputFileName: str
#     instrumentType: str = ''
#     measurementType: str = ''
#     minMax: list = field(default_factory=lambda:[-np.inf,np.inf])
#     Overwrite: int = 0
#     dependent: int = ''
#     inputFileName_dates: list = field(default_factory=list)
#     instrument: str = ''
#     instrumentSN: list = field(default_factory=list)
#     loggedCalibration: list = field(default_factory=list)
#     currentCalibration: list = field(default_factory=list)
#     comments: str = ''
#     zeroPt: float = -9999


# @dataclass(kw_only=True)
# class Trace:
#     # The expected fields and their corresponding types for a trace object
#     # metadata field instructs behavior
#     # Standard T/F (True for all parameter defined by default, False for non-standard parameters parsed from ini)
#     # Stage controls which parameters are written:
#     #   * common > always written
#     #   * firststage > always written (for first stage)
#     #   * secondstage > always written (for second stage)
#     #       * optional only written if provided

#     # Required for all 
#     variableName: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':False})
#     title: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':None})
#     units: str = field(default='', metadata={'standard':True,'optional':False,'stage':'common','literal':None})
#     # Required for first stage
#     inputFileName: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False}) # Note, can be a list instead if needed?  matlab codebase has variable as cell array but not sure why?
#     instrumentType: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
#     measurementType: str = field(default='', metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
#     minMax: list = field(default_factory=list, metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
#     zeroPt: list = field(default_factory=lambda:[-9999], metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
#     # Required for second stage
#     Evaluate: str = field(default='', metadata={'standard':True,'optional':False,'stage':'secondstage','literal':True})
#     # Optional parameters
#     # ONLY required for optionals we want to have predefined settings
#     # Can take any non-defined field, but defining here will give defaults for standardization
#     Overwrite: int = field(default=0, metadata={'standard':True,'optional':False,'stage':'firststage','literal':False})
#     dependent: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
#     originalVariable: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':True})
#     postEvaluate: str = field(default='', metadata={'standard':True,'optional':True,'stage':'secondstage','literal':True})
#     comment: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':True})
#     ECCC_station: str = field(default='', metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
#     inputFileName_dates: list = field(default_factory=list, metadata={'standard':True,'optional':True,'stage':'firststage','literal':False})
    
#     # Hidden (parameters to control behaviour which will not be written)
#     # by default, repr should be true, but when setting globals trace-by-trace, will set to false
#     repr: bool = field(default=True,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
#     stage: str = field(default='firststage',repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
#     fields_on_the_fly: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
#     verbose: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})
#     # If file being parsed is an include,
#     # Use variable substitution for globalVariables instead of anchors (limited to within one-file)
#     include: bool = field(default=False,repr=False,metadata={'standard':True,'optional':False,'stage':None,'literal':False})



# @dataclass(kw_only=True)
# class firstStageIni(baseClass):
#     siteID: str = field(repr=False)
#     Metadata: dict = field(default_factory=dict)
#     globalVars: dict = field(default_factory=dict)
#     Trace: dict = field(default_factory=dict)
#     Include: dict = field(default_factory=dict)


