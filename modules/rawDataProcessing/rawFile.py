from dataclasses import dataclass, field
# from src.helperFunctions.baseClass import baseClass
from modules.helperFunctions.baseClass import baseClass

@dataclass(kw_only=True)
class rawFile(baseClass):
    UID: str = None

    def __post_init__(self):
        if self.UID is None:
            self.configFileName = type(self).__name__
        else:
            self.configFileName = f"{type(self).__name__}_{self.UID}"
        super().__post_init__()
