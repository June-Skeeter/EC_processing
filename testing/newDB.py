import os
import time
import shutil
import context

import dateparser

import modules.database.project as project
import modules.database.site as site
import modules.database.dataSource as dataSource
import modules.database.sensorModels as sensorModels
from modules.rawDataProcessing.ecf32 import ecf32

T1 = time.time()


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)


pr = project.projectConfiguration(
    projectPath=projectPath,
    createdBy='JS',
    verbose=False)


si = site.siteConfiguration(
    verbose=False,
    projectPath=projectPath,
    siteID='BBS',
    startDate='2023-06-10',
    endDate='2024-05-30',
    latitude = '49.12930679',
    longitude = '-122.9849701',
    altitude = 4.0,
    siteName = 'Burns Bog Seedling Site',
    PI = 'June Skeeter',
    description = 'Post-fire lodgeable pine seedling stand',)


sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
ds = dataSource.dataSourceConfiguration(
    verbose=False,
    projectPath=projectPath,
    siteID='BBS',
    dataSourceID='EC',
    measurementSystem={'measurementType':'EC',
                       'dataLogger':'CR1000',
                       'sensorConfigurations':[
            sensorModels.CSAT3(
                measurementHeight=4.25,
                northOffset=135.0,
                ),
            sensorModels.LI7500(xSeparation=0.158,ySeparation=-0.031,verticalSeparation=0.0),
            sensorModels.LI7500(xSeparation=0.128,ySeparation=10.031,verticalSeparation=0.0),]},
    sourceFileTemplate=sourceFileName
)


ecf32(projectPath=projectPath,siteID='BBS',dataSourceID='EC',verbose=False,fileName=sourceFileName)

# sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')

sc = site.siteConfiguration(
    verbose=False,
    projectPath=projectPath,
    siteID='SCL',
    startDate=dateparser.parse(
        '2024-07-10',
        settings={'DATE_ORDER':'YMD','RETURN_AS_TIMEZONE_AWARE':True}),
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    altitude = 1.0,
    siteName = 'Swiss Cheese Lake',
    PI = 'June Skeeter & Peter Morse',
    description = 'Wet sedge meadow, continuous permafrost',
    )


T2 = time.time()
print(f"runtime = {(T2-T1)}")



breakpoint()

