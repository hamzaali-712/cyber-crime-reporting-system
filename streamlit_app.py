"""
Root entry point for Streamlit Cloud deployment.
Streamlit Cloud must be pointed at THIS file (streamlit_app.py), NOT frontend/app.py.

Why this file exists:
  - Streamlit Cloud runs from the repo root.
  - When the entry point is `frontend/app.py`, the `frontend` package is NOT
    on sys.path, so `from frontend.views.xxx import ...` fails.
  - By using this root-level file, the repo root is always the CWD and
    `frontend` is a proper importable package.
"""
import sys
import pathlib

# ── Guarantee repo root is first on sys.path ──────────────────────────────────
ROOT_DIR = pathlib.Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# ── Delegate entirely to frontend/app.py ──────────────────────────────────────
# We exec the file rather than importing it so that:
#   1. st.set_page_config() is the very first Streamlit call (required).
#   2. __name__ == "__main__" semantics are preserved.
#   3. No circular-import or module-aliasing issues arise.
import runpy
runpy.run_path(str(ROOT_DIR / "frontend" / "app.py"), run_name="__main__")