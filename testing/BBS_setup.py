import os
import shutil
import dateparser
import context
import modules.rawDataProcessing.parseCSI as parseCSI
import modules.databaseSetup.configurations as configurations
import modules.databaseSetup.systemTypes as systemTypes
import modules.databaseSetup.sensorModels as sensorModels
from modules.rawDataProcessing.ecf32 import ecf32

# print(sensorModels.IRGASON(measurementHeight=4.25,northOffset=135).toConfig(majorOrder=-1,keepNull=False))

data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


sm = sensorModels.CSI_T107(traceMetadataMap={'TA_1_1_1':{'measurementType':'temperature'}})

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)

configurations.projectConfiguration(
    projectPath=projectPath,
    createdBy='JS',
    verbose=False
)


sc = configurations.siteConfiguration(
    verbose=False,
    projectPath=projectPath,
    siteID='BBS',
    startDate='2023-06-10',
    endDate='2024-05-30',
    latitude = 49.12930679,
    longitude = -122.9849701,
    altitude = 4.0,
    siteName = 'Burns Bog Seedling Site',
    PI = 'June Skeeter',
    description = 'Post-fire lodgeable pine seedling stand',
    )


sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')

