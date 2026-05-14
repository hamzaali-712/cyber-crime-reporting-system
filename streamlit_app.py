"""Streamlit Cloud entry point — delegates 100% to frontend/app.py."""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import runpy
runpy.run_path(str(ROOT / "frontend" / "app.py"), run_name="__main__")