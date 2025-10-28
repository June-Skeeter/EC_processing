import os
import yaml
import context
import shutil
from src.highFrequency import epf32


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)

sourceFileName = os.path.join(data,'57840_Time_Series_40.dat')
# sourceFileName = os.path.join(data,'TOA5_BBS.FLUX_2023_08_01_1530.dat')

print('Testing highfrequency data load from file: {}\n'.format(sourceFileName))



hf = epf32.epf32(
    projectPath=projectPath,
    sourceFileName=sourceFileName,
    siteID='SCL',
    sourceFileType='TOB3',
    sonicAnemometer= 'IRGASON',
    )
# breakpoint()
# print(yaml.safe_dump(hf.__dict__))