import os
import yaml
import context
import shutil
from src.dbFunctions.project import project,projectConfiguration
from src.dbFunctions.site import site
from src.dbFunctions.measurement import measurement
from ruamel.yaml import YAML
import time

yaml = YAML()


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))
shutil.rmtree(projectPath, ignore_errors=True)

# pC = projectConfiguration(projectPath=projectPath)#,siteIDs=['SCL','FIL','ILL'])
# project(projectPath=projectPath)

s = measurement(projectPath=projectPath,siteID='SCL',measurementID='highFrequency')
# s = measurement(projectPath=projectPath,siteID='SCL',measurementID='fluxes')
# s = measurement(projectPath=projectPath,siteID='SCL',measurementID='bioMet')

# print(s.config.description)
# print(site())

# print('Test creation of new site')

# with open(os.path.join(data,'SCL_siteConfiguration.yml')) as f:
#     kwargs = yaml.load(f)
# print(kwargs)
# siteConfiguration.siteConfiguration(projectPath=projectPath,siteID='SCL')
# siteConfiguration.siteConfiguration(projectPath=projectPath,siteID='SCL')

# siteConfiguration.siteConfiguration(
#     projectPath=projectPath,
#     **kwargs
#     )
# testRead = siteConfiguration.siteConfiguration(
#     projectPath=projectPath,
#     siteID='SCL'
# )
# print('clear old',os.path.join(data,'projectTemplate'))
# shutil.rmtree(os.path.join(data,'projectTemplate'),ignore_errors=True)
# shutil.copytree(projectPath,os.path.join(data,'projectTemplate'))