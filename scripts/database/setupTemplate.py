

import scripts.database.project as project
import scripts.database.site as site
import scripts.database.dataSource as dataSource

# projectPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'outputs','test'))
project.projectConfiguration.template(projectPath=projectPath)
site.siteConfiguration.template(projectPath=projectPath)
dataSource.dataSourceConfiguration.template(projectPath=projectPath)
# sys.exit()