import os
import yaml
import shutil

import context
from src.siteSetup.siteObjects import *


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)


# dO = defaultObject.from_dict({'index': 1,
#                               'UID': 'SCL',
#                              'latitude': 'N69 13.5850',
#                              'longitude': 'W135 15.1144',
#                              'altitude': 1.0})

# print(dO.__dict__)


# testLogger()

sM = siteMetadata(
    UID = 'SCL',
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    altitude = 1.0,
    siteName = 'Swiss Cheese Lake',
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    measurementInventory = [
        {'model':'testLogger',},
        testLogger()
        ]
    )
print(sM.measurementInventory)

# print(sM.__dict__)
# breakpoint()
# sM = siteMetadata(**sM.__dict__)
# print(sM.__dict__)