import os
import time
import shutil
import context
import context
import scripts.rawDataProcessing.parseCSV as parseCSV
import scripts.database.dataSource as dataSource
import scripts.database.sensorModels as sensorModels


fpath = [r'testing\data\20750528-SHSC.SSM.SGT.240720_240913readout.csv',r'testing\data\20750527-SHSC.WSM.SGT.csv']
# fpath = r'testing\data\20750527-SHSC.WSM.SGT.csv'
data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','deltaEC'))

# os.remove(r'C:\Users\jskeeter\gsc-permafrost\EC_processing\testing\outputs\deltaEC\siteMetadata\SCL\dataSources\HOBO_SSM_sourceConfig.yml')

ds = dataSource.dataSourceConfiguration(
    configReset=True,
    verbose=False,
    projectPath=projectPath,
    siteID='SCL',
    dataSourceID='HOBO_TS',
    measurementType='BIOMET',
    templateFile=fpath ,
    filenameMatch = '*SHSC.*.SGT*.csv',
    fileFormat = 'HOBOcsv',
    dataLogger='HOBO',
    sensorInventory=[sensorModels.thermocouple()]*8,
    description='Salix Sedge Meadow Temperature Profile',
        traceMetadata={
            'Date Time, GMT+00:00':{
                'measurementType':'TIMESTAMP',
                'ignore':True
            },
            '*20750528*LBL: 5)':{
            'units':'deg c',
            'variableName':'TS_SSM_5cm',
            'sensorID':'thermocouple_1'
            },
            '*20750528*LBL: 25)':{
            'units':'deg c',
            'variableName':'TS_SSM_25cm',
            'sensorID':'thermocouple_2'
            },
            '*20750528*LBL: 50)':{
            'units':'deg c',
            'variableName':'TS_SSM_50cm',
            'sensorID':'thermocouple_3'
            },
            '*20750528*LBL: 100)':{
            'units':'deg c',
            'variableName':'TS_SSM_100cm',
            'sensorID':'thermocouple_4'
            },
            '*20750527*LBL: 5)':{
            'units':'deg c',
            'variableName':'TS_SSM_5cm',
            'sensorID':'thermocouple_5'
            },
            '*20750527*LBL: 25)':{
            'units':'deg c',
            'variableName':'TS_SSM_25cm',
            'sensorID':'thermocouple_6'
            },
            '*20750527*LBL: 50)':{
            'units':'deg c',
            'variableName':'TS_SSM_50cm',
            'sensorID':'thermocouple_7'
            },
            '*20750527*LBL: 100)':{
            'units':'deg c',
            'variableName':'TS_SSM_100cm',
            'sensorID':'thermocouple_8'
            }
        }
    )


# pc = parseCSV.HOBOcsv(fileName=fpath,
#                  timestampName='Date Time, GMT+00:00',
#                  traceMetadata={
#                      '*LBL: 5)':{
#                         'units':'deg c',
#                         'variableName':'TS_5cm'
#                      },
#                      '*LBL: 25)':{
#                         'units':'deg c',
#                         'variableName':'TS_25cm'
#                      },
#                      '*LBL: 50)':{
#                         'units':'deg c',
#                         'variableName':'TS_50cm'
#                      },
#                      '*LBL: 100)':{
#                         'units':'deg c',
#                         'variableName':'TS_100cm'
#                      }
#                  }
#                  )
breakpoint()

# def loadVal(val=None):
#     print(val)

# def wrapper():
#     return(loadVal)

# @dataclass
# class baseClass:
#     load1: Callable = loadVal
#     load2: Callable = field(default_factory=lambda: loadVal)
    
# bc = baseClass()

# bc.load1('it works')
# bc.load2('it works')
