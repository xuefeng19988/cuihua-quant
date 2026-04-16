"""
Daily Report Generator
Generates a text summary of today's performance and signals.
"""

import os
import sys
import requests
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from dotenv import load_dotenv

class DailyReporter:
    def __init__(self):
        load_dotenv(os.path.join(project_root, '.env'))
        self.webhook_url = os.getenv('WECOM_WEBHOOK')
        
    def generate_content(self, signals):
        """Generate text content for the report"""
        content = f"# 📊 Cuihua Quant Daily Report\n"
        content += f"Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        if not signals:
            content += "No signals generated today."
            return content
            
        content += "## 📈 Top Signals\n"
        for i, sig in enumerate(signals[:5]):
            content += f"{i+1}. **{sig['code']}**: Score {sig['score']:.1f} ({', '.join(sig['signals'])})\n"
            
        return content
        
    def send_wecom(self, content):
        """Send report to WeCom"""
        if not self.webhook_url:
            print("⚠️  WECOM_WEBHOOK not configured.")
            return
            
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "content": content
            }
        }
        
        try:
            resp = requests.post(self.webhook_url, json=payload)
            print(f"📤 Report sent: {resp.status_code}")
        except Exception as e:
            print(f"❌ Send failed: {e}")
