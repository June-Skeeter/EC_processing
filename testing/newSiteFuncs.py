import os
import yaml
import shutil

import context
from src.databaseObjects.project import project
from src.siteSetup.siteObjects import *
# from src.siteSetup.loggerObjects import *
from src.siteSetup.sensorObjects import *
# from src.readData.dataSource import *
import src.siteSetup.loggerObjects as loggerObjects
import src.siteSetup.sensorObjects as sensorObjects
# from src.readData.parseCSI import TOB3, TOA5
import src.readData as readData


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)



sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')
# df = readData.parseCSI.TOB3(sourceFileName=sourceFileName,extractData=False)#.saveConfigFile()

# # sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
# # df = readData.parseCSI.TOA5(sourceFileName=sourceFileName,extractData=False).saveConfigFile()

sM = siteMetadata(
    projectPath=projectPath,
    siteID = 'SCL',
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    startDate = '2024-07-10',
    altitude = 1.0,
    siteName = 'Swiss Cheese Lake',
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    dataLoggers=[
        loggerObjects.HOBO(
            name ='SSM',
            latitude = 'N 69 13.5239',
            longitude = 'W135 15.1358',
            sensors = [
                thermcouple(name='5cm'),
                thermcouple(name='10cm'),
                thermcouple(name='50cm'),
                thermcouple(name='100cm'),
                       ]
            ),
        loggerObjects.HOBO(
            name='WSM',
            latitude = 'N 69 13.5521',
            longitude = 'W135 15.1350',
            sensors = [thermcouple()]*4
            ),
        loggerObjects.CR1000x(
            serialNumber=57840,
        ),
    ],
    # dataSources = [
    #     # readData.parseCSI.TOB3(sourceFileName=sourceFileName,extractData=False),
    #     # CR1000x(
    #     #     sensorInventory=[
    #     #         sonicAnemometer(
    #     #             northOffset=38,
    #     #             measurementHeight=2.78)]
    #     # ),
    #     # HOBO(),
    #     # manualMeasurement()
    #     ],
    verbose=False
    )


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
