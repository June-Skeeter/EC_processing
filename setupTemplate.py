import os
import shutil
import scripts.database.project as project
import scripts.database.site as site
import scripts.database.dataSource as dataSource
from submodules.helperFunctions.cmdParse import cmdParse

defaultArgs = {'projectPath':os.getcwd(),'siteID':[]}
args = cmdParse(defaultArgs)

if args['projectPath'] == 'test' and os.path.isdir(args['projectPath']):
    shutil.rmtree(args['projectPath'])

args = {}

fp = project.projectConfiguration.template(kwargs=args)
cl = project.project.fromTemplate(fp)
print(cl)
# if len(args['siteID'])==0:
#     args.pop('siteID')
site.siteConfiguration.template(kwargs=args)
# else:
#     for id in args['siteID']:
#         kwargs = args.copy()
#         kwargs['siteID'] = id
#         site.siteConfiguration.template(kwargs=kwargs)