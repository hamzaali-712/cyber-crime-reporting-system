"""
Root entry point for Streamlit Cloud deployment.
Delegates to frontend/app.py
"""
import sys
import pathlib

# Add project root to path
ROOT_DIR = pathlib.Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Run the main app
from frontend.app import main
main()