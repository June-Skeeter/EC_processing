import os
import yaml
import context
import shutil
from src.dbFunctions.project import project,projectConfiguration
from src.dbFunctions.site import site,siteConfiguration
from src.dbFunctions.instruments import IRGASON_sonic,IRGASON_irga,LI7700#Inventory
# from src.dbFunctions.measurement import measurement
from ruamel.yaml import YAML
import time

yaml = YAML()


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)

# pC = projectConfiguration(projectPath=projectPath)#,siteIDs=['SCL','FIL','ILL'])
# project(projectPath=projectPath)

# s = measurement(projectPath=projectPath,siteID='SCL',measurementID='highFrequency')
# s = measurement(projectPath=projectPath,siteID='SCL',measurementID='fluxes')
# s = measurement(projectPath=projectPath,siteID='SCL',measurementID='bioMet')


# with open(os.path.join(data,'SCL_siteConfiguration.yml')) as f:
#     kwargs = yaml.load(f)

print(IRGASON_sonic(measurementHeight=3.0,northOffset=38))
# print(irga_open(model='IRGASON'))
print(IRGASON_irga())
print(LI7700(northwardSeparation=5,eastwardSeparation=5,verticalSeparation=0))
# instrumentInventory(
#     projectPath=projectPath,
#     siteID='SCL',
#     # _instruments=1
# )
# breakpoint()
# iI = instrumentInventory(
#     projectPath=projectPath,
#     siteID='SCL',
#     # _instruments=1
# )


# breakpoint()

# siteConfiguration(
#     projectPath = projectPath,
#     siteID = 'SCL',
#     dateEstablished = '2024-07-10',
#     siteName = 'Swiss Cheese Lake',
#     latitude = 69.2264167,
#     longitude = -135.2519067,
#     altitude = 1.0,
#     PI = 'June Skeeter & Peter Morse',
#     description = 'Wet sedge meadow, continuous permafrost',
#     )


# breakpoint()

# sc = siteConfiguration(projectPath=projectPath,siteID='SCL')

# siteConfiguration.siteConfiguration(
#     projectPath=projectPath,
#     **kwargs
#     )
# testRead = siteConfiguration.siteConfiguration(
#     projectPath=projectPath,
#     siteID='SCL'
# )

# shutil.rmtree(os.path.join(data,'projectTemplate'),ignore_errors=True)
# shutil.copytree(projectPath,os.path.join(data,'projectTemplate'))