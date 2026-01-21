import os
import sys
import time
import shutil
import context
import dateparser
import modules.database.project as project
import modules.database.site as site
import modules.database.dataSource as dataSource
import modules.database.sensorModels as sensorModels
from modules.rawDataProcessing.ecf32 import ecf32
from modules.database.dbTools import dbDump,database,firstStage
from modules.rawDataProcessing.parseCSI import TOB3

T1 = time.time()

# fs = firstStageTrace(inputFileName='ftest',measurementType='BIOMET')
# print(fs.to_dict())


# projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
# firstStage(projectPath=projectPath,siteID='SCL')

test = True
if test:
    data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

    shutil.rmtree(projectPath, ignore_errors=True)

# db = database(projectPath=projectPath,siteID = 'SCL',stageID='BIOMET')
# db.dbYear(year=2025)
# sourceFileName = os.path.join(data,'Met_Data121.dat') 
# dbDump(projectPath=projectPath,siteID='SCL',dataSourceID='BIOMET_2024',fileName=sourceFileName)

    shutil.rmtree(projectPath, ignore_errors=True)

    pr = project.projectConfiguration(
        projectPath=projectPath,
        createdBy='JS',
        verbose=False)

    sc = site.siteConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        startDate='2024-07-10 00:00:00-00:00',
        latitude = 'N69 13.5850',
        longitude = 'W135 15.1144',
        altitude = 1.0,
        siteName = 'Swiss Cheese Lake',
        PI = 'June Skeeter & Peter Morse',
        description = 'Wet sedge meadow, continuous permafrost',
        )
    
    sourceFileName = os.path.join(data,'Met_Data120.dat') 
    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='BIOMET_V1',
        measurementType='BIOMET',
        # startDate='2024-07-10 00:00:00+00:00',
        endDate='2024-09-15 00:00:00+00:00',
        sourceSystemMetadata = dataSource.sourceSystemMetadata(
            dataLogger='CR1000X',
            sensorConfigurations=[
                sensorModels.VoltDiff(),
                sensorModels.HMP155(measurementHeight=3),
                sensorModels.BaroVue(),
                sensorModels.PLS()
            ]+[sensorModels.thermocouple()]*3),
        sourceFileMetadata={
            'fileName':sourceFileName,
            'traceMetadata':{'AirTC_Avg':{'variableName':'TA_1_1_1'}}}#,'sensorID':'HMP_1'}}}
    )

    sys.exit()
    dbDump(projectPath=projectPath,siteID='SCL',dataSourceID='BIOMET_V1',fileName=sourceFileName)

    # breakpoint()
    # sourceFileName = os.path.join(data,'Met_Data121.dat') 
    # dbDump(projectPath=projectPath,siteID='SCL',dataSourceID='BIOMET_V1',fileName=sourceFileName)


    # sourceFileName = os.path.join(data,'Flux_Data1426.dat') 
    # dataSource.dataSourceConfiguration(
    #     verbose=False,
    #     projectPath=projectPath,
    #     siteID='SCL',
    #     dataSourceID='EC_V1',
    #     measurementType='EC',
    #     # startDate='2024-07-10 00:00:00-00:00',
    #     endDate='2024-09-15 00:00:00-00:00',
    #     sourceSystemMetadata = dataSource.sourceSystemMetadata(
    #         dataLogger='CR1000X',
    #         sensorConfigurations=[
    #             sensorModels.CSAT3(
    #                 measurementHeight=4.25,
    #                 northOffset=135.0,
    #                 ),
    #             sensorModels.LI7500(xSeparation=0.158,ySeparation=-0.031,verticalSeparation=0.0),
    #         ]),
    #     sourceFileMetadata=sourceFileName
    # )

    # ecf32(projectPath=projectPath,siteID='SCL',dataSourceID='EC_V1',verbose=False,fileName=sourceFileName)


    # sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')


    # dataSource.dataSourceConfiguration(
    #     verbose=False,
    #     projectPath=projectPath,
    #     siteID='SCL',
    #     dataSourceID='EC_2025',
    #     sourceSystemMetadata = dataSource.EasyFlux_IRGASON_LI7700(
    #         measurementHeight=3.26,
    #         northOffset=33.0,
    #         xSeparation=0.41,
    #         ySeparation=0.16,
    #         zSeparation=0.0
    #     ),
    #     sourceFileMetadata=sourceFileName
    # )

    # ecf32(projectPath=projectPath,siteID='SCL',dataSourceID='EC_2025',verbose=False,fileName=sourceFileName)



    # si = site.siteConfiguration(
    #     verbose=False,
    #     projectPath=projectPath,
    #     siteID='BBS',
    #     startDate='2023-06-10',
    #     endDate='2024-05-30',
    #     latitude = '49.12930679',
    #     longitude = '-122.9849701',
    #     altitude = 4.0,
    #     siteName = 'Burns Bog Seedling Site',
    #     PI = 'June Skeeter',
    #     description = 'Post-fire lodgeable pine seedling stand',)


    # sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
    # ds = dataSource.dataSourceConfiguration(
    #     verbose=False,
    #     projectPath=projectPath,
    #     siteID='BBS',
    #     dataSourceID='EC',
    #     sourceSystemMetadata={'measurementType':'EC',
    #                     'dataLogger':'CR1000',
    #                     'sensorConfigurations':[
    #             sensorModels.CSAT3(
    #                 measurementHeight=4.25,
    #                 northOffset=135.0,
    #                 ),
    #             sensorModels.LI7500(xSeparation=0.158,ySeparation=-0.031,verticalSeparation=0.0),
    #             sensorModels.LI7500(xSeparation=0.128,ySeparation=10.031,verticalSeparation=0.0),]},
    #     sourceFileMetadata=sourceFileName
    # )


    # ecf32(projectPath=projectPath,siteID='BBS',dataSourceID='EC',verbose=False,fileName=sourceFileName)


setup = False
if setup:
    data = r'D:\data-dump\SCL'
    if not os.path.isdir(data):
        data = r"U:\data-dump\SCL"#os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
        if not os.path.isdir(data):
            sys.exit('invalid dir')
    projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','myProject'))
    
    shutil.rmtree(projectPath, ignore_errors=True)

    pr = project.projectConfiguration(
        projectPath=projectPath,
        createdBy='JS',
        verbose=False)
    
    
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

    # 2024 Met data
    sourceDir = os.path.join(data,'2024') 
    sourceFiles = []
    for dir,_,fn in os.walk(sourceDir):
        sourceFiles = sourceFiles + [os.path.join(dir,f) for f in fn if f.startswith('Met_')]
        


    sourceFileName = os.path.join(sourceDir,sourceFiles[0])
    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='SCL_V1',
        measurementType='BIOMET',
        sourceSystemMetadata = dataSource.sourceSystemMetadata(
            # measurementType='BIOMET',
            dataLogger='CR1000X',
            sensorConfigurations=[
                sensorModels.VoltDiff(),
                sensorModels.HMP155(measurementHeight=3),
                sensorModels.BaroVue(),
                sensorModels.PLS()
            ]+[sensorModels.thermocouple()]*3,
            verbose=False),
        sourceFileMetadata=sourceFileName
    )
    for f in sourceFiles[:2]:
        # print('writing: ',f)
        sourceFileName = os.path.join(sourceDir,f)
        dbDump(projectPath=projectPath,siteID='SCL',dataSourceID='SCL_V1',fileName=sourceFileName,verbose=False)

    breakpoint()

    

    sourceFileName = os.path.join(data,'20240912','Flux_Data1426.dat') 
    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='EC_2024',
        sourceSystemMetadata = dataSource.sourceSystemMetadata(
            measurementType='EC',
            dataLogger='CR1000X',
            sensorConfigurations=[
                sensorModels.CSAT3(
                    measurementHeight=4.25,
                    northOffset=135.0,
                    ),
                sensorModels.LI7500(xSeparation=0.158,ySeparation=-0.031,verticalSeparation=0.0),
            ]),
        sourceFileMetadata=sourceFileName
    )

    ecf32(projectPath=projectPath,siteID='SCL',dataSourceID='EC_2024',verbose=False,fileName=sourceFileName)



    # 2025 Met data
    sourceDir = os.path.join(data,'2025','20250806') 
    sourceFiles = [os.path.join(sourceDir,f) for f in os.listdir(sourceDir) if 'CSFormat' in f]
    sourceDir = os.path.join(data,'2025','20250910') 
    sourceFiles = sourceFiles+[os.path.join(sourceDir,f) for f in os.listdir(sourceDir) if 'CSFormat' in f]
    sourceDir = os.path.join(data,'2025','20250927') 
    sourceFiles = sourceFiles+[os.path.join(sourceDir,f) for f in os.listdir(sourceDir) if 'CSFormat' in f]
    sourceFileName = sourceFiles[-1]

    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='EasyFlux_2025',
        sourceSystemMetadata = dataSource.sourceSystemMetadata(
            measurementType='BIOMET',
            dataLogger='CR1000X',
            sensorConfigurations=[
                sensorModels.CSAT3(
                    measurementHeight=4.25,
                    northOffset=135.0,
                    ),
                sensorModels.LI7500(xSeparation=0.158,ySeparation=-0.031,verticalSeparation=0.0),
            ],
            verbose=False),
        sourceFileMetadata=sourceFileName
    )

    for f in sourceFiles:
        # print('writing: ',f)
        # sourceFileName = os.path.join(sourceDir,f)
        dbDump(projectPath=projectPath,siteID='SCL',dataSourceID='EasyFlux_2025',fileName=f,verbose=False)

T2 = time.time()
print(f"runtime = {(T2-T1)}")



# breakpoint()

