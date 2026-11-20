from pathlib import Path
import shutil
root=Path(__file__).resolve().parents[1]
shutil.copytree(root/'frontend/dist',root/'dist',dirs_exist_ok=True)
