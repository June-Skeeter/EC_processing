import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import submodules
import scripts

data = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

FL = os.listdir(data)
for f in FL:
    if f.endswith('.zip'):
        if f.replace('.zip', '.dat') not in FL:
            import zipfile
            with zipfile.ZipFile(os.path.join(data, f), 'r') as zip_ref:
                zip_ref.extractall(data)
