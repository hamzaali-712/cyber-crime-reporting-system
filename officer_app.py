"""Streamlit entry point for the Officer Portal."""
import sys
import pathlib

ROOT     = pathlib.Path(__file__).resolve().parent
FRONTEND = ROOT / "frontend"

# Add paths before running anything else
for _p in [str(ROOT), str(FRONTEND)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import runpy
runpy.run_path(str(FRONTEND / "officer_app.py"), run_name="__main__")
