import zipfile
import os
filename = r'C:/Users/jskeeter/gsc-permafrost/EC_processing/testing/data/2017-08-10T093000_AIU-1697.ghg'
dout = r'C:/Users/jskeeter/gsc-permafrost/EC_processing/testing/data/ghgout'
with zipfile.ZipFile(filename,'r') as zf:
    os.makedirs(dout,exist_ok=True)
    zf.extractall(path=dout)