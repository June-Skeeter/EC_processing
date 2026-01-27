import context

import src.readData as readData

import submodules.helperFunctions as helperFunctions
f = readData.parseCSI.csiLogger(fileType=None).saveConfigFile()
print(f)
# print(readData.traceObject.trace(variableName='test', units='m', dtype='float'))
