import os
import yaml
import shutil

import context
from src.databaseObjects.project import project
import src.siteSetup.ecSystem as ecSystem
import src.siteSetup.biometSystem as biometSystem
import src.databaseObjects.defaultObjects as defaultObjects
import src.siteSetup.loggerObjects as loggerObjects
import src.siteSetup.siteObjects as siteObjects
import src.readData.parseCSI as parseCSI
import src.readData.dataSource as dataSource


setup = False


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
if setup:
    shutil.rmtree(projectPath, ignore_errors=True)

    Flux = ecSystem.ecSystem(
        siteID = 'SCL',
        measurementHeight=3.38,
        northOffset=33.0,
        dataLogger=loggerObjects.CR1000X(),
        sensors = [
            ecSystem.IRGASON(),
            ecSystem.LI7700(xSeparation=0.41,ySeparation=0.16,zSeparation=0.0)
            ],
        )

    BIOMET = biometSystem.biometSystem(
        siteID = 'SCL',
        dataLogger=loggerObjects.CR1000X(),
        sensors = [
            biometSystem.SN500(),
        ]
        )


    EC = siteObjects.siteObject(
        siteID='SCL',
        projectPath=projectPath,
        latitude = 'N69 13.5850',
        longitude = 'W135 15.1144',
        startDate = '2024-07-10',
        altitude = 1.0,
        siteName = 'Swiss Cheese Lake',
        PI = 'June Skeeter & Peter Morse',
        description = 'Wet sedge meadow, continuous permafrost',
        dataSystems=[
            Flux,
            BIOMET
        ]
    )

# sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')
# df = parseCSI.TOB3(
#     siteID='SCL',
#     systemID='SCL_EC_1',
#     projectPath=projectPath,
#     sourceFileName=sourceFileName,
#     extractData=False)


    Flux = ecSystem.ecSystem(
        siteID = 'BBS',
        measurementHeight=4.25,
        northOffset=135,
        dataLogger=loggerObjects.CR1000(),
        sensors = [
            ecSystem.CSAT3(),
            ecSystem.LI7500(xSeparation=0.41,ySeparation=0.16,zSeparation=0.0)
            ],
        )

    BIOMET = biometSystem.biometSystem(
        siteID = 'BBS',
        dataLogger=loggerObjects.CR1000X(),
        sensors = [
            biometSystem.SN500(),
        ]
        )


    EC = siteObjects.siteObject(
        siteID='BBS',
        projectPath=projectPath,
        latitude = 'N49.25',
        longitude = 'W123',
        startDate = '2023-06-15',
        altitude = 2.0,
        siteName = 'Burns Bog Seedling',
        PI = 'June Skeeter',
        description = 'Lodgepole Pine Seedlings',
        dataSystems=[
            Flux,
            BIOMET
        ]
    )


    sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
    df = parseCSI.TOA5(
        projectPath=projectPath,
        siteID='BBS',
        templateFileName=sourceFileName,
        systemID='BBS_EC_1',
        extractData=False
        )#.saveConfigFile()

sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
df = parseCSI.TOA5(
    projectPath=projectPath,
    siteID='BBS',
    sourceFileName=sourceFileName,
    systemID='BBS_EC_1',
    extractData=False

)

breakpoint()

































# IRGASON_irga()

# sM = siteMetadata(
#     projectPath=projectPath,
#     siteID = 'SCL',
#     latitude = 'N69 13.5850',
#     longitude = 'W135 15.1144',
#     startDate = '2024-07-10',
#     altitude = 1.0,
#     siteName = 'Swiss Cheese Lake',
#     PI = 'June Skeeter & Peter Morse',
#     description = 'Wet sedge meadow, continuous permafrost',
#     dataLoggers=[
#         loggerObjects.HOBO(
#             name ='SSM',
#             latitude = 'N 69 13.5239',
#             longitude = 'W135 15.1358',
#             sensors = [
#                 thermocouple(name='5cm'),
#                 thermocouple(name='10cm'),
#                 thermocouple(name='50cm'),
#                 thermocouple(name='100cm'),
#                        ]
#             ),
#         loggerObjects.HOBO(
#             name='WSM',
#             latitude = 'N 69 13.5521',
#             longitude = 'W135 15.1350',
#             sensors = [
#                 thermocouple(name='5cm'),
#                 thermocouple(name='10cm'),
#                 thermocouple(name='50cm'),
#                 thermocouple(name='100cm'),
#                        ]
#             ),
#         loggerObjects.CR1000x(
#             serialNumber=57840,
#             sensors = [
#                 IRGASON_sonic(
#                     measurementHeight=3.38,
#                     northOffset=33.0),
#                 IRGASON_irga(),
#                 LI7700(
# Const SEPARATION_X_GA_77 = -0.41
# Const SEPARATION_Y_GA_77 = 0.16)
#             ]
#         ),
#     ],
#     # dataSources = [
#     #     # readData.parseCSI.TOB3(sourceFileName=sourceFileName,extractData=False),
#     #     # CR1000x(
#     #     #     sensorInventory=[
#     #     #         sonicAnemometer(
#     #     #             northOffset=38,
#     #     #             measurementHeight=2.78)]
#     #     # ),
#     #     # HOBO(),
#     #     # manualMeasurement()
#     #     ],
#     verbose=False
#     )


# breakpoint()
# sM = siteMetadata(
#     projectPath=projectPath,
#     siteID='SCL'
#     )
# breakpoint()



# sM = siteMetadata(
#     projectPath=projectPath,
#     siteID = 'SCL',
#     latitude = 'N69 13.5850',
#     longitude = 'W135 15.1144',
#     startDate = '2024-07-10',
#     altitude = 1.0,
#     siteName = 'Swiss Cheese Lake',
#     PI = 'June Skeeter & Peter Morse',
#     description = 'Wet sedge meadow, continuous permafrost',
#     dataSources = [
#         # CR1000x(),
#         {'model':'CR1000x'},
#         # HOBO(),
#         # manualMeasurement()
#         ],
#     verbose=False
#     )

# print(sM.logFile)
# sM = siteMetadata(
#     validate=False,
#     configFile=os.path.join(projectPath,'SCL','siteMetadata.yml'),
#     siteID = 'SCL',

# ).config()
# print(sM)

# sM = siteMetadata()
# print(siteMetadata.template())
