"""
WSGI Entry Point - 翠花量化 REST API Server
前后端分离架构 - api_server.py + Vue 前端
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.web.api_server import app
