import os
import sys
import yaml
import context
import shutil
from src.highFrequency import epf32
from src.dbFunctions import site
from src.dbFunctions import measurement
from src.dbFunctions import instruments


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)
# shutil.copytree(os.path.join(data,'projectTemplate'),projectPath)

# instruments.instrumentInventory(
#     projectPath=projectPath,
#     siteID='SCL',
#     startDate='2024-07-10')

# sonic = measurement.sonicAnemometer(model='CSAT3',measurementHeight=4.75,northOffset=138)

# breakpoint()
# sys.exit()

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