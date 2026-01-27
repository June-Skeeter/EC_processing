from dataclasses import dataclass,field
from typing import Callable

def loadVal(val=None):
    print(val)

def wrapper():
    return(loadVal)

@dataclass
class baseClass:
    load1: Callable = loadVal
    load2: Callable = field(default_factory=lambda: loadVal)
    
bc = baseClass()

bc.load1('it works')
bc.load2('it works')
