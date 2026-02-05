import os
import sys
import inspect
from typing import Iterable
from types import MappingProxyType
from datetime import datetime, timezone
from dataclasses import dataclass, field
from submodules.helperFunctions.baseClass import baseClass
from zoneinfo import ZoneInfo
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

yaml = YAML()

mdMap = baseClass.metadataMap

@dataclass(kw_only=True)
class project(baseClass):
    projectPath: str = field(metadata=mdMap('Root path of the current project'))
    subPath: str = field(default='',repr=False,init=False)
    configName: str = field(default=None,init=False,repr=False)
    lastModified: str = field(default=None,repr=False,metadata=mdMap('Last time configuration file was modified programmatically, does not account for manual user-modifications'))


    def __post_init__(self):
        if self.projectPath is None:
            return
        self.projectPath = os.path.normpath(self.projectPath)
        if not type(self).__name__.endswith('Configuration'):
            self.syncConfig(projectConfiguration.from_dict(self.__dict__))
        if self.configName is not None:
            self.configFilePath = os.path.normpath(os.path.join(self.projectPath,self.subPath,self.configName))
        super().__post_init__()

    def syncConfig(self,config):
        config = config.from_dict(self.to_dict(keepNull=False)|{'projectPath':self.projectPath,'verbose':self.verbose,'debug':self.debug,'readOnly':self.readOnly})
        exclude = list(baseClass.__dataclass_fields__.keys()) + [k for k,v in project.__dataclass_fields__.items() if not v.repr]
        
        for key,value in config.__dict__.items():
            if (key not in exclude #and value is not None 
                and (key not in self.__dict__.keys() or self.__dict__[key] is None)
                ):
                setattr(self,key,value)

    @classmethod
    def template(cls,projectPath=None):
        if not cls.__name__.endswith('Configuration'):
            sys.exit('template generation is only for configuration classes')
        if projectPath is None:
            sys.exit('Provide project path to generate template file')
        # Fill required args with variable name
        signature = inspect.signature(cls.__init__)
        required_args = {'projectPath':projectPath,
                         'lastModified':baseClass.currentTimeString()}
        for param in signature.parameters.values():
            # Exclude 'self' and parameters with default values
            if param.name not in ['self','projectPath'] and param.default is param.empty:
                required_args[param.name] = param.name
        hiddenDefaults = {'typeCheck':False,'readOnly':True,'fromFile':False}
        kwargs = required_args|hiddenDefaults    
        template = cls.from_dict(kwargs)
        templateFilePath = template.configFilePath
        template = template.to_dict()
        data = CommentedMap()
        for key,value in template.items():
            data[key] = value

            comment = f'datatype={cls.__dataclass_fields__[key].type.__name__}; '
            # if len( cls.__dataclass_fields__[key].metadata.items()) == 0:
            #     sys.exit(f"{cls.__name__}: {key} missing metadata")
            for desc,com in cls.__dataclass_fields__[key].metadata.items():

                comment = comment + f"{desc}={com}; "
            data.yaml_add_eol_comment(comment,key=key)
        baseClass().saveDict(data,templateFilePath,header=cls.__dataclass_fields__['header'].default)
        # os.makedirs(os.path.split(templateFilePath)[0],exist_ok=True)
        # with open(templateFilePath,'w') as f:
        #     f.write(cls.__dataclass_fields__['header'].default)
        #     yaml.dump(data,f)


@dataclass(kw_only=True)
class configCommon:
    lastModified: str = field(default=None,metadata=mdMap('last time configuration file was modified programmatically'))
    fromFile: bool = field(default=True,repr=False)
    readOnly: bool = field(default=False, repr=False)


headerText = f'''
Project configuration file gives the overarching context of the project
Defines the parameters which are common across all aspects of the project
Should require minimal user-modification once created
Created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
'''


@dataclass(kw_only=True)
class projectConfiguration(configCommon,project):

    header: str = field(default=headerText,repr=False,init=False) # YAML header, must be treated 
    createdBy: str = field(default='',metadata=mdMap('Name of project creator'))
    projectDescription: str = field(default='',metadata=mdMap('Description of the project'))



    def __post_init__(self):
        self.configName = 'projectConfiguration.yml'
        super().__post_init__()
        if os.path.isdir(self.projectPath) and not os.path.exists(self.configFilePath) and len(os.listdir(self.projectPath))!=0:
            self.logError(f'Error: Cannot initiate new project in non-empty directory: {self.projectPath}')

        # Only save if it is first time creating
        # Otherwise saves are performed where appropriate in child classes
        # if not self.configFileExists or not self.readOnly:
        if not self.readOnly:
            self.logWarning('Saving')
            self.saveConfigFile()
