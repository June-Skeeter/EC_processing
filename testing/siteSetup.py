import os
import yaml
import context
import shutil
from src.dbFunctions.project import project,projectConfiguration
# from src.dbFunctions.site import site,siteConfiguration
# from src.dbFunctions.sensor import *
from src.dbFunctions.sensorList import *
from src.dbFunctions.loggerList import *
# from src.dbFunctions.dataset import *
from src.dbFunctions.pointObjects import *
# from src.dbFunctions.measurement import measurement
from ruamel.yaml import YAML
import time

yaml = YAML()

data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)

pO = pointObject(
    UID='PO1',
    latitude= 'N69 13.5850',
    longitude= 'W135 15.1144',
    altitude=1.0
)

sM = siteMetadata(
    UID = 'SCL',
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    altitude = 1.0,
    siteName = 'Swiss Cheese Lake',
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    measruementInventory= [
        testLogger(
        model='CR1000x',
        # sensorInventory=[
        #     testSensor(
        #         model='CSAT3')]
        )])

print(sM.__dict__)
breakpoint()
sM = siteMetadata(**sM.__dict__)
print(sM.__dict__)

# siteConfiguration(
#     projectPath = projectPath,
#     siteID = 'SCL',
#     startDate = '2024-07-10',
#     siteName = 'Swiss Cheese Lake',
#     latitude = 69.2264167,
#     longitude = -135.2519067,
#     altitude = 1.0,
#     PI = 'June Skeeter & Peter Morse',
#     description = 'Wet sedge meadow, continuous permafrost',
#     dataSources = [
#         CR1000x(
#             sourceType='Flux',
#             sensorInventory = [
#                 CSAT3(
#                     measurementHeight=3.0,
#                     northOffset=38,
#                     # startDate='2024-07-10',
#                     endDate='2024-09-15'
#                     ),
#                 LI7500(
#                     northwardSeparation=5,
#                     eastwardSeparation=5,
#                     verticalSeparation=0,
#                     # startDate='2024-07-10',
#                     endDate='2024-09-15'
#                     ),
#                 IRGASON_sonic(
#                     measurementHeight=3.0,
#                     northOffset=38,
#                     startDate='2025-08-02'
#                     ),
#                 IRGASON_irga(
#                     startDate='2025-08-02'
#                     ),
#                 LI7700(
#                     # startDate='2024-07-10',
#                     northwardSeparation=5,
#                     eastwardSeparation=5,
#                     verticalSeparation=0
#                     ),
#                 ]
#             ),
#         HOBO(
#             sensorInventory = [
#                 genericSensor(
#                     model='Thermocouple',
#                     manufacturer='Onset')
#             ]
#         ),
#         HOBO(),
#         ]
#     )


# print('\n\n\n\nReading!\n\n\n\n')

# sc = siteConfiguration(projectPath=projectPath,siteID='SCL')
