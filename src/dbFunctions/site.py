import os
import sys
from .project import project
from dataclasses import dataclass, field
from typing import Iterable
from datetime import datetime, timezone
from ..helperFunctions.baseClass import baseClass
from ..helperFunctions.dictFuncs import dcToDict
from .dataset import callDataset


default_comment = f'''
Site configuration file
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class siteConfiguration(project):
    header: str = field(default=default_comment,repr=False) # YAML header, must be treated differently
    siteID: str
    siteName: str = None
    latitude: float = None
    longitude: float = None
    altitude: float = None
    PI: str = None
    description: str = None
    startDate: datetime = None
    # sensorInventory: Iterable = field(default_factory=dict)
    dataSources: Iterable = field(default_factory=dict)
    
    def __post_init__(self):
        # baseClass will load configuration from this path if it exists
        self.configFile = os.path.join(self.projectPath,'Sites',self.siteID,type(self).__name__+'.yml')
        super().__post_init__()
        if self.typeCheck:
            self.measurementCheck()     

        self.saveToYaml()

    def measurementCheck(self):
        # All measurements are associated with a logger (even if the logger is a human :D)
        if type(self.dataSources) is dict:
            self.dataSources = list(self.dataSources.values())
        Inventory = {}
        for measurement in self.dataSources:
            # print('Date')
            # breakpoint()
            if type(measurement) is dict:
                measurement = callDataset(measurement['sourceID'])(**measurement)
            i = 2
            while measurement.sourceID in Inventory.keys():
                measurement.UID(i)
                i+=1
            if measurement.startDate is None:
                self.logWarning(f'No start date provided for {measurement.sourceID}')
                measurement.startDate = self.startDate
            Inventory[measurement.sourceID] = dcToDict(measurement,inheritance=True,repr=True)
        self.dataSources = Inventory

    # # def sensorCheck(self):
    # #     if type(self.sensorInventory) is dict:
    # #         self.sensorInventory = list(self.sensorInventory.values())
    # #     Inventory = {}
    #     for sensorData in self.sensorInventory:
    #         if type(sensorData) is dict:
    #             # if sensorData['model'] == 'BIRGASON':
                # #     breakpoint()
        #         # sensorData = callSensor(sensorData['sensorID'])(**sensorData)
        #         # print(sensorData.model)
        #     i = 2
        #     while sensorData.sensorID in Inventory.keys():
        #         sensorData.UID(i)
        #         i+=1
                
        #     if sensorData.startDate is None:
        #         self.logWarning(f'No installation date provided for {sensorData.sensorID}')
        #         self.logChoice(f'Default to startDate ({self.startDate}) or provide alternate date')
        #         sensorData.startDate = self.startDate
        #     Inventory[sensorData.sensorID] = dcToDict(sensorData,inheritance=True,repr=True)
        # self.sensorInventory = Inventory


@dataclass(kw_only=True)
class site(baseClass):
    projectPath: str
    siteID: str
    siteConfig: siteConfiguration = None
    # safeMode: bool = True

    def __post_init__(self):
        self.siteConfig = siteConfiguration(projectPath=self.projectPath,siteID=self.siteID,safeMode=self.safeMode)
        # self.syncAttributes(self.siteConfig,overwrite=True)
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