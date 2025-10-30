import os
from .site import site
from dataclasses import dataclass, field
from datetime import datetime, UTC
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict


default_comment = f'''
Measurement configuration file
Created: {datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class trace:
    name: str = 'name'
    unit: str = 'unit'

@dataclass(kw_only=True)
class measurementConfiguration(site):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    measurementID: str
    measurementName: str = None
    latitude: float = None
    longitude: float = None
    description: str = None
    variables: dict = field(default_factory=dict)

    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,'Sites',self.siteID,'Measurements',type(self).__name__+'.yml')
        super().__post_init__()
        if self.variables == self.__dataclass_fields__['variables'].default_factory():
            tmp = trace()
            self.variables[tmp.name] = dcToDict(tmp,repr=True,inheritance=False)
        # self.variables = {v:trace.__dict__ for v in self.variables}
        self.saveToYaml()

@dataclass(kw_only=True)
class measurement(baseFunctions):
    projectPath: str
    siteID: str
    measurementID: str
    # variables: list = field(default_factory=lambda:[])
    config: measurementConfiguration = None

    def __post_init__(self):
        # print(self.variables)
        self.config = measurementConfiguration(
            projectPath=self.projectPath,
            siteID=self.siteID,
            measurementID=self.measurementID,
            # variables=self.variables
            )
        super().__post_init__()
