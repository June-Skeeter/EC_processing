import os
import yaml
import shutil

import context
from src.siteSetup.siteObjects import *
# from src.siteSetup.loggerObjects import *
from src.siteSetup.sensorObjects import *
from src.siteSetup.dataSource import *


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)

sM = siteMetadata(
    configFile=os.path.join(projectPath,'SCL','siteMetadata.yml'),
    siteID = 'SCL',
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    startDate = '2024-07-10',
    altitude = 1.0,
    siteName = 'Swiss Cheese Lake',
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    dataSources = [
        CR1000x(),
        {'model':'CR1000x'},
        HOBO(),
        manualMeasurement()
        ]
    )

# print(sM)

# sM = siteMetadata()
# print(siteMetadata.template())
