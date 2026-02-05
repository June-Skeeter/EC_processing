import os
import sys
import time
import shutil
import context
import numpy as np
import matplotlib.pyplot as plt
import scripts.database.project as project
import scripts.database.site as site
import scripts.database.dataSource as dataSource
import scripts.database.sensorModels as sensorModels
from scripts.rawDataProcessing.ecf32 import ecf32
from scripts.rawDataProcessing.parseCSI import TOB3
from scripts.database.dbTools import database
import inspect

import yaml

template = True
if template:
    projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','test'))
    project.projectConfiguration.template(projectPath=projectPath)
    site.siteConfiguration.template(projectPath=projectPath)
    dataSource.dataSourceConfiguration.template(projectPath=projectPath)
    sys.exit()

configFile = r"C:\Users\User\GSC_Work\EC_processing\testing\SCL_setup.yml"
projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','test'))
with open(configFile) as config:
    print(yaml.safe_load(config))

# from dataclasses import dataclass
# @dataclass
# class te:
#     a: str = 'a'

#     def __post_init__(self):
#         print('b')
#         self.x()

#     def x(self=None):
#         print('t')

# te.x()
# te()