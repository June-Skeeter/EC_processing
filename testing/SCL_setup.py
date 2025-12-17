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


# # configurations.dataSourceConfiguration(
# #     projectPath=projectPath,
# #     siteID='SCL',
# #     dataSourceID ='EC_2024',
# #     systemConfiguration = systemTypes.EC(
# #         traceMetadataMap='CSI_LI7500_default',
# #         dataLogger = 'CR1000X',
# #         sensorConfigurations=[
# #             sensorModels.CSAT3(
# #                 measurementHeight=3.28,
# #                 northOffset=33.0,
# #                 ),
# #             sensorModels.LI7500(
# #                 northwardSeparation=-0.06,
# #                 eastwardSeparation=0.15,
# #                 verticalSeparation=0.0
# #                 ),
# #             sensorModels.LI7700(
# #                 northwardSeparation=0.13,
# #                 eastwardSeparation=0.23,
# #                 verticalSeparation=0.04
# #             )
# #         ]
# #     ),
# #     sourceFile = os.path.join(data,'Flux_Data1426.dat')
# # )


# configurations.dataSourceConfiguration(
#     projectPath=projectPath,
#     siteID='SCL',
#     dataSourceID ='EC_2025',
#     systemConfiguration = systemTypes.IRGASON_LI7700(
#         measurementHeight=3.26,
#         northOffset=33.0,
#         xSeparation=0.41,
#         ySeparation=0.16,
#         zSeparation=0.0
#     ),
#     sourceFile=os.path.join(data,'57840_Time_Series_40.dat'),
# )

# # ecf32(projectPath=projectPath,siteID='SCL',dataSourceID='EC_2024',verbose=False)

# ecf32(projectPath=projectPath,siteID='SCL',dataSourceID='EC_2025',verbose=False,fileName=os.path.join(data,'57840_Time_Series_40.dat'))




