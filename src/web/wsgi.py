"""
Production WSGI Entry Point
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.web.dashboard import create_app
app = create_app()
