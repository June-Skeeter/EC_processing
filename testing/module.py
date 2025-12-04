import os
import shutil
import context
import modules.rawDataProcessing.parseCSI as parseCSI
import modules.databaseSetup.configurations as configurations
# from modules.databaseSetup.site import siteConfiguration,site

data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))


projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)

configurations.siteConfiguration(
    projectPath=projectPath,
    siteID='SCL',
    startDate='2024-07-10',
    latitude = 'N69 13.5850',
    longitude = 'W135 15.1144',
    )

# siteConfiguration(projectPath=projectPath,siteID='SCL')
# site(projectPath=projectPath,siteID='SCL')


# sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')
# df = parseCSI.TOB3(
#     # siteID='SCL',
#     # systemID='SCL_EC_1',
#     configFileRoot=projectPath,
#     sourceFileName=sourceFileName,
#     extractData=False,
#     verbose=None)
# breakpoint()


# sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')
# df = parseCSI.TOA5(
#     configFileRoot=projectPath,
#     sourceFileName=sourceFileName,
#     extractData=False,
#     verbose=None)