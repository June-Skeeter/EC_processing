import os
from .site import site
from dataclasses import dataclass, field
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict


default_comment = f'''
Measurement configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class trace(baseFunctions):
    variableNumber: int = field(default=1,repr=False) # Counter variable to represent position (in source file or processing order)
    variableName: str
    units: str = None
    dtype: str = None
    instrumentID: str = None
    ignore: bool = False
    minMax: list = field(default_factory=list)
    sensorID: str = None

    def __post_init__(self):
        return super().__post_init__()

@dataclass(kw_only=True)
class measurementConfiguration(site):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    measurementID: str
    measurementName: str = None
    latitude: float = None
    longitude: float = None
    description: str = None
    samplingInterval: float = None  # in seconds
    samplingFrequency: str = None # in Hz
    variables: dict = field(default_factory=dict)

    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,'Sites',self.siteID,'Measurements',self.measurementID+'.yml')
        super().__post_init__()
        varFormat = {}
        for i, (key,values) in enumerate(self.variables.items()):
            values = {k:v for k,v in values.items() if k in trace.__annotations__.keys()}
            traceFormat = trace(variableNumber=i+1,**values)
            varFormat[traceFormat.variableNumber] = dcToDict(traceFormat,repr=True,inheritance=False)
        self.variables = varFormat
        self.saveToYaml()

@dataclass(kw_only=True)
class genericMeasurement(baseFunctions):
    projectPath: str
    siteID: str
    measurementID: str
    variables: dict = field(default_factory=lambda:{'example':{'variableName':'example'}})
    # config: measurementConfiguration = None

    def __post_init__(self):
        config = measurementConfiguration(
                projectPath=self.projectPath,
                siteID=self.siteID,
                measurementID=self.measurementID,
                variables=self.variables
                )
        self.syncAttributes(config,overwrite=False,inheritance=True)
        super().__post_init__()

@dataclass(kw_only=True)
class eddyCovarianceMeasurement(baseFunctions):
    projectPath: str
    siteID: str
    measurementID: str = 'highFrequency'
    # sonic: sonicAnemometer = None
    sonicNorthOffset: float = None
    sonicAnemometer: str = field(default=None,metadata={
    'description': 'Indicates the type of file (see options)',
    'options':['IRGASON','CSAT3','CSAT3B']})
    # IRGA


    def __post_init__(self):
        config = measurementConfiguration(
                projectPath=self.projectPath,
                siteID=self.siteID,
                measurementID=self.measurementID,
                variables=self.dataColumns
                )
        self.syncAttributes(config,overwrite=False,inheritance=True)
        super().__post_init__()
            
