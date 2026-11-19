# termoyazd browser scientific runtime

Pyodide 0.27.7 core and bundled Python 3.12 / NumPy 2.0.2 / SciPy 1.14.1 / OpenBLAS 0.3.26 are sourced from the official Pyodide release distribution at https://cdn.jsdelivr.net/pyodide/v0.27.7/full/ . iapws 1.5.5 wheel is from PyPI. Python package licenses are retained inside their original wheels/distributions. Scientific application source is synchronized from backend/app by scripts/sync-browser-engine.py. Requests run sequentially; first load is relatively large. This is a real Python computation engine, not prerecorded output.
