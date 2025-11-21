import os
import sys
import yaml
import context
import shutil
from src.highFrequency import epf32
from src.dbFunctions.site import siteConfiguration
from src.dbFunctions.sensor import *


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)


siteConfiguration(
    projectPath = projectPath,
    siteID = 'SCL',
    dateEstablished = '2024-07-10',
    siteName = 'Swiss Cheese Lake',
    latitude = 69.2264167,
    longitude = -135.2519067,
    altitude = 1.0,
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    sensorInventory=[
        CSAT3(
            measurementHeight=3.0,
            northOffset=38,
            startDate='2024-07-10',
            endDate='2024-09-15'
            ),
        LI7500(
            northwardSeparation=5,
            eastwardSeparation=5,
            verticalSeparation=0,
            startDate='2024-07-10',
            endDate='2024-09-15'
            ),
        IRGASON_sonic(
            measurementHeight=3.0,
            northOffset=38,
            startDate='2025-08-02'
            ),
        IRGASON_irga(
            startDate='2025-08-02'
            ),
        LI7700(
            startDate='2024-07-10',
            northwardSeparation=5,
            eastwardSeparation=5,
            verticalSeparation=0
            ),
    ]
    )

breakpoint()

sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
# epf32.test(projectPath=projectPath)
hf = epf32.epf32(
    projectPath=projectPath,
    sourceFileName=sourceFileName,
    siteID='SCL',
    sourceFileType='TOA5',
    sonicAnemometer= 'IRGASON',
    startDate='2024-07-10'    
    )


# sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')
# hf = epf32.epf32(
#     projectPath=projectPath,
#     sourceFileName=sourceFileName,
#     siteID='SCL',
#     sourceFileType='TOB3',
#     sonicAnemometer= 'IRGASON',
#     )


# breakpoint()