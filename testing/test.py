import os
import time
import shutil
import context
import context
import scripts.rawDataProcessing.parseCSV as parseCSV


fpath = r'testing\data\20750528-SHSC.SSM.SGT.240720_240913readout.csv'
# fpath = r'testing\data\20750527-SHSC.WSM.SGT.csv'

parseCSV.HOBOcsv(fileName=fpath,
                 timestampName='Date Time, GMT+00:00',
                #  timestampFormat={"Date Time, GMT+00:00":"%y/%m/%d %H:%M:%S"},
                 )

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
