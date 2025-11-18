import os
import sys
from .project import project
# from ..helperFunctions.parseCoordinates import parseCoordinates
from dataclasses import dataclass, field
# from ruamel.yaml import YAML
from datetime import datetime, timezone
from ..helperFunctions.baseFunctions import baseFunctions
from ..helperFunctions.dictFuncs import dcToDict
from .instruments import instrument#Inventory#, sonicAnemometer, gasAnalyzer, metInstrument


default_comment = f'''
Site configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''

@dataclass(kw_only=True)
class testDC:
    a: int = 1
    b: str = 'a'
    c: str = None

    def __post_init__(self):
        self.c = self.b

@dataclass(kw_only=True)
class siteConfiguration(project):
    dependencies = {'ba':1}
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    siteID: str
    siteName: str = None
    siteName: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None
    PI: str = None
    description: str = None
    dateEstablished: datetime = None
    instrumentation: dict = field(default_factory=lambda:{'example':instrument()})
    
    def __post_init__(self):
        # baseFunctions will load configuration from this path if it exists
        self.yamlConfigFile = os.path.join(self.projectPath,'Sites',self.siteID,type(self).__name__+'.yml')
        super().__post_init__()
        self.instruemntCheck()
        # # Default setup, to be edited manually
        # self.instrumentInventory = {
        #     self.dateEstablished:dcToDict(sonicAnemometer(model='IRGASON'),repr=True,inheritance=False)}
        # print(self.instrumentInventory)
        # iSet = instrumentInventory(startDate=self.dateEstablished)

        # self.instrumentation[iSet.version] = iSet.configuration
        # # self.instrumentInventory[iSet.startDate] = dcToDict(iSet,repr=True,inheritance=False)
        

        self.saveToYaml()

    def instruemntCheck(self):
        for key,value in self.instrumentation.items():
            if type(value)!=instrument:
                value = instrument(**value)
            self.instrumentation[key] = dcToDict(value,repr=True,inheritance=False)
        breakpoint()


@dataclass(kw_only=True)
class site(baseFunctions):
    projectPath: str
    siteID: str
    siteConfig: siteConfiguration = None

    def __post_init__(self):
        self.siteConfig = siteConfiguration(projectPath=self.projectPath,siteID=self.siteID)
        self.syncAttributes(self.siteConfig,overwrite=True)
        super().__post_init__()
        
# # Template for multiple inheritance post init calls
# @dataclass(kw_only=True)
# class T1:
#     a: int = 1.1

#     def __post_init_T1__(self):
#         self.a=self.a*self.c

# @dataclass(kw_only=True)
# class T2:
#     b: str = 0

#     def __post_init_T2__(self):
#         self.b=self.b+.01

# @dataclass(kw_only=True)
# class T3(T1, T2):
#     c: float = 3.3

#     def __post_init__(self):
        
#         super().__post_init_T1__()
#         super().__post_init_T2__()
#         self.c*=self.b