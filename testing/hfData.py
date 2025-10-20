import os
import yaml
import context
import shutil
from src.highFrequency import epf32


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)

sourceFile = os.path.join(data,'57840_Time_Series_40.dat')
print('Testing highfrequency data load from file: {}\n'.format(sourceFile))

hf = epf32.epf32(
    projectPath=projectPath,
    sourceFile=sourceFile,
    siteID='SCL',
    )

# print(yaml.safe_dump(hf.__dict__))