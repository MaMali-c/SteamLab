from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
for name in ['__init__.py','engine.py','thermo.py','plotting.py']:
    shutil.copy2(root/'backend/app'/name,root/'frontend/public/python'/name)
