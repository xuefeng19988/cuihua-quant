"""
Production WSGI Entry Point
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.web.webui_v3 import create_webui_v3
app = create_webui_v3()
