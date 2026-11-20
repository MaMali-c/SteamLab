"""The same unittest scientific checks are also collected by pytest."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'validation'))
from run_validation import EngineChecks
