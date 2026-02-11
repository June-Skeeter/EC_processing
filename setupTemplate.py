import os
import shutil
import scripts.database.project as project
import scripts.database.site as site
import scripts.database.dataSource as dataSource
from submodules.helperFunctions.cmdParse import cmdParse

defaultArgs = {'projectPath':os.getcwd(),'siteID':[]}
args = cmdParse(defaultArgs)

# if args['projectPath'] == 'test' and os.path.isdir(args['projectPath']):
#     shutil.rmtree(args['projectPath'])

# args = {}

# fp = project.projectConfiguration.template(kwargs=args)
# sp = site.siteConfiguration.template(kwargs=args)

# dp = dataSource.dataSourceConfiguration.template(kwargs=args)
# cl = dataSource.dataSourceConfiguration.fromTemplate(dp)

prj = project.projectConfiguration.from_yaml(r'C:\Users\jskeeter\gsc-permafrost\EC_processing\projectPath\projectConfiguration.yml',kwargs={'projectPath':'projectPath'})
print(prj)