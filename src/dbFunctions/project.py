import os
import sys
import yaml
from datetime import datetime
from dataclasses import dataclass, field
from ..helperFunctions.typeEnforcer import typeEnforcer

@dataclass(kw_only=True)
class project(typeEnforcer):
    projectPath: str
    databaseInterval: int = 1800 # in seconds
    creationDate: str = field(default_factory=lambda: datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'))
    safeMode: bool = True # If True, prevents overwriting existing files without warning.

    def pathCheck(self):
        if not os.path.isdir(self.projectPath) or os.listdir(self.projectPath)==[]:
            os.makedirs(self.projectPath, exist_ok=True)
            os.makedirs(os.path.join(self.projectPath,'Sites'), exist_ok=True)
            with open(os.path.join(self.projectPath,'ecDbConfig.yml'),'w') as f:
                yaml.safe_dump({'creationDate':self.creationDate,'lastModified':self.creationDate},f)
        elif not os.path.isfile(os.path.join(self.projectPath,'ecDbConfig.yml')):
            sys.exit('Database path {} exists but is missing ecDbConfig.yml file. Please check.'.format(self.projectPath))
            
