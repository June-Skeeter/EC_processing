import os
import time
import shutil
import context
import scripts.database.project as project
import scripts.database.site as site
import scripts.database.dataSource as dataSource
import scripts.database.sensorModels as sensorModels
from scripts.rawDataProcessing.ecf32 import ecf32
from scripts.rawDataProcessing.parseCSI import TOB3
from scripts.database.dbTools import database


T1 = time.time()

data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','deltaEC'))


# fn = r"C:\Users\User\GSC_Work\EC_processing\testing\data\MetaData115.dat"
# md = TOB3(fileName=fn)
# breakpoint()

reset = False
if reset:
    shutil.rmtree(projectPath, ignore_errors=True)

    project.projectConfiguration(
        projectPath=projectPath,
        createdBy='June Skeeter',
        projectDescription='Sandbox for testing analysis of Swiss Cheese Lake Data',
        verbose=False)

    site.siteConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        startDate='2024-07-10 00:00:00',
        latitude = 'N69 13.5850',
        longitude = 'W135 15.1144',
        altitude = 1.0,
        siteName = 'Swiss Cheese Lake',
        PI = 'June Skeeter & Peter Morse',
        description = 'Wet sedge meadow, continuous permafrost',
        canopyHeight=0.4,
        )


    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='BIOMET_V1',
        measurementType='BIOMET',
        # startDate='2024-07-10 00:00:00+00:00',
        endDate='2024-09-15 00:00:00+00:00',
        templateFile=os.path.join(data,'Met_Data120.dat') ,
        filenameMatch = 'Met_*.dat',
        fileFormat = 'TOB3',
        dataLogger='CR1000X',
        sensorInventory=[
            sensorModels.HMP155(measurementHeight=3,variables=['AirTC_Avg','RH']),
            sensorModels.NRLite(measurementHeight=1,variables=['NetRad_Avg','NetRad_Corrected_Avg']),
            sensorModels.LI200x(measurementHeight=1,variables=['SlrW_Avg']),
            sensorModels.PLS(),
            sensorModels.BaroVue()
            ]+[sensorModels.thermocouple()]*3,
        traceMetadata = {
            'AirTC_Avg':{'variableName':'TA_1_1_1'},
            'RH':{'variableName':'RH_1_1_1'},
            'NetRad_Avg':{'ignore':True},
            'NetRad_Corrected_Avg':{'variableName':'NETRAD_1_1_1'},
            }
        )

    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='EC_V1',
        measurementType='EC',
        # startDate='2024-07-10 00:00:00+00:00',
        endDate='2024-09-15 00:00:00+00:00',
        templateFile=os.path.join(data,'Flux_Data1426.dat') ,
        filenameMatch = 'Flux_*.dat',
        fileFormat = 'TOB3',
        dataLogger='CR1000X',
        sensorInventory=[sensorModels.CSAT3(
                            measurementHeight=3.285,
                            northOffset=33.0,
                            variables=['Ux','Uy','Uz','Ts','Diagnostic_CSAT']
                            ),
                        sensorModels.LI7500(
                            xSeparation=0.15,
                            ySeparation=-0.06,
                            verticalSeparation=0.0,
                            variables=["CO2","CO2","press","LI7500_diag","LI7550_SignalStrength"]
                            ),
                        sensorModels.LI7700(
                            xSeparation=0.23,
                            ySeparation=-0.13,
                            verticalSeparation=0.04,
                            variables=["Diagnostic_7700","CH4_density","CH4_mole_fraction","Temperature","Pressure","RSSI"]),
        ],
        traceMetadata = {
            "CO2":{'measurementType':'molar_density'},
            "CO2":{'measurementType':'molar_density'},
            "CH4_density":{'measurementType':'molar_density'},
            "CH4_mole_fraction":{'measurementType':'mixing_ratio'},
            "seconds":{'ignore':True},
            "nanoseconds":{'ignore':True},
            }
        )


    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='BIOMET_V2',
        measurementType='BIOMET',
        startDate='2025-07-10 00:00:00+00:00',
        endDate='2025-10-03 00:00:00+00:00',
        templateFile=os.path.join(data,'57840_Flux_CSFormat_24.dat') ,
        filenameMatch = '*CSFormat*.dat',
        fileFormat = 'TOB3',
        dataLogger='CR1000X',
        sensorInventory=[
            sensorModels.HMP155(measurementHeight=3,variables=['TA_1_1_3','RH_1_1_3']),
            sensorModels.SN500(measurementHeight=3,variables=["NETRAD","ALB","SW_IN","SW_OUT","LW_IN","LW_OUT"]),
            sensorModels.CS310(measurementHeight=3,variables=["PPFD_IN"]),
            sensorModels.IRGASON(measurementHeight=3.26,sensorFamily='BIOMET',variables=['TA_1_1_1','USTAR',"TKE",'WS','WD'])
            ],
        traceMetadata = {
            'NETRAD':{'variableName':'NETRAD_1_1_1'},
            'PPFD_IN':{'variableName':'PPFD_IN_1_1_1'},
            'SW_IN':{'variableName':'SW_IN_1_1_1'},
            'LW_IN':{'variableName':'LW_IN_1_1_1'},
            'SW_OUT':{'variableName':'SW_OUT_1_1_1'},
            'LW_OUT':{'variableName':'LW_OUT_1_1_1'},
            'LAB':{'variableName':'LAB_1_1_1'},
            }
    )


    dataSource.dataSourceConfiguration(
        verbose=False,
        projectPath=projectPath,
        siteID='SCL',
        dataSourceID='EC_V2',
        measurementType='EC',
        startDate='2025-07-10 00:00:00+00:00',
        endDate='2025-10-03 00:00:00+00:00',
        templateFile=os.path.join(data,'57840_Time_Series_40.dat') ,
        filenameMatch = '*Time_Series*.dat',
        fileFormat = 'TOB3',
        dataLogger='CR1000X',
        sensorInventory=[sensorModels.IRGASON(
                            measurementHeight=3.285,
                            northOffset=33.0,
                            variables=["Ux","Uy","Uz","T_SONIC","diag_sonic","CO2_density","CO2_density_fast_tmpr","H2O_density","diag_irga","T_SONIC_corr","TA_1_1_1","PA","CO2_sig_strgth","H2O_sig_strgth"]
                            ),
                        sensorModels.LI7700(
                            xSeparation=-0.41,
                            ySeparation=-0.16,
                            verticalSeparation=0,
                            variables=["LI7700_CH4D","LI7700_pressure","LI7700_temperature","LI7700_sig_strgth","LI7700_diag"]),
        ],
        traceMetadata = {
            "CO2_density":{'measurementType':'molar_density'},
            "H2O_density":{'measurementType':'molar_density'},
            "LI7700_CH4D":{'measurementType':'molar_density'},
            }
    )


# ds = dataSource.dataSource(
#     projectPath=projectPath,
#     siteID='SCL',
#     dataSourceID='BIOMET_V1',
#     )

# searchDir = r'C:\Users\User\GSC_Work\SCL_2024'
# searchDir = r'U:\data-dump\SCL\2024'
# ds.dbDump(
#     sourceDir=searchDir)


ds = dataSource.dataSource(
    projectPath=projectPath,
    siteID='SCL',
    dataSourceID='BIOMET_V2',
    )

searchDir=r'U:\data-dump\SCL\2025'

ds.dbDump(
    sourceDir=searchDir)


dbf = database(projectPath=projectPath).readSiteData(siteID='SCL',stageID='BIOMET/BIOMET_V2')
# print(dbf)

import matplotlib.pyplot as plt

plt.figure()
plt.plot(dbf['WS']*3.6)
plt.grid()
plt.show()


