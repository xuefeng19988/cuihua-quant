"""
Existing Scripts Integrator
Integrates existing scripts from skills/news-daily into the new system.
"""

import os
import sys
import subprocess
import yaml
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

# Existing scripts directory
EXISTING_SCRIPTS = os.path.join(project_root, '../skills/news-daily/scripts')

class ExistingScriptsIntegrator:
    """
    Integrates existing scripts into the new system.
    Provides unified API to call old scripts.
    """
    
    def __init__(self):
        self.scripts = {
            'realtime_predict': os.path.join(EXISTING_SCRIPTS, 'futu_realtime_predict.py'),
            'stock_close_predict': os.path.join(EXISTING_SCRIPTS, 'stock_close_predict.py'),
            'prediction_accuracy': os.path.join(EXISTING_SCRIPTS, 'prediction_accuracy_analysis.py'),
            'quant_optimization': os.path.join(EXISTING_SCRIPTS, 'quant_comprehensive_optimization.py'),
            'quant_recent_train': os.path.join(EXISTING_SCRIPTS, 'quant_recent_train.py'),
        }
        
    def run_script(self, name: str, args: List[str] = None, timeout: int = 120) -> Dict:
        """Run an existing script."""
        script_path = self.scripts.get(name)
        if not script_path or not os.path.exists(script_path):
            return {'status': 'ERROR', 'message': f'Script not found: {name}'}
            
        cmd = ['python3', script_path]
        if args:
            cmd.extend(args)
            
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=project_root
            )
            return {
                'status': 'OK' if result.returncode == 0 else 'ERROR',
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'status': 'TIMEOUT', 'message': f'Script {name} timed out after {timeout}s'}
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}
            
    def run_all_predictions(self) -> Dict:
        """Run all prediction-related scripts."""
        results = {}
        
        # Realtime predict
        results['realtime'] = self.run_script('realtime_predict')
        
        # Stock close predict
        results['close_predict'] = self.run_script('stock_close_predict')
        
        return results
        
    def update_prediction_accuracy(self, date: str = None) -> Dict:
        """Update prediction accuracy analysis."""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        return self.run_script('stock_close_predict', ['--update-actual', date])
        
    def get_available_scripts(self) -> List[str]:
        """Get list of available existing scripts."""
        available = []
        for name, path in self.scripts.items():
            if os.path.exists(path):
                available.append(name)
        return available
        
    def generate_integration_report(self) -> str:
        """Generate report of available existing scripts."""
        lines = []
        lines.append("=" * 50)
        lines.append("📦 现有脚本集成报告")
        lines.append("=" * 50)
        
        available = self.get_available_scripts()
        lines.append(f"\n✅ 可用脚本: {len(available)}/{len(self.scripts)}")
        
        for name, path in self.scripts.items():
            status = "✅" if os.path.exists(path) else "❌"
            lines.append(f"  {status} {name}")
            lines.append(f"     {path}")
            
        return "\n".join(lines)


if __name__ == "__main__":
    integrator = ExistingScriptsIntegrator()
    print(integrator.generate_integration_report())
