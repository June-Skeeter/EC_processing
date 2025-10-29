import os
import yaml
import context
import shutil
from src.dbFunctions.project import newProject
from src.dbFunctions import siteAttributes
from ruamel.yaml import YAML

yaml = YAML()


data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','testProject'))

shutil.rmtree(projectPath, ignore_errors=True)

# siteAttributes.siteAttributes(
#     projectPath=projectPath,
# )

newProject(projectPath=projectPath)

# print('Test creation of new site')

# with open(os.path.join(data,'SCL_siteAttributes.yml')) as f:
#     kwargs = yaml.load(f)
# print(kwargs)
# siteAttributes.siteAttributes(
#     projectPath=projectPath,
#     **kwargs
#     )
# testRead = siteAttributes.siteAttributes(
#     projectPath=projectPath,
#     siteID='SCL'
# )
# print('clear old',os.path.join(data,'projectTemplate'))
# shutil.rmtree(os.path.join(data,'projectTemplate'),ignore_errors=True)
# shutil.copytree(projectPath,os.path.join(data,'projectTemplate'))