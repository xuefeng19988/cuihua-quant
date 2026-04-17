"""
Phase 42: Automated Workflow Engine
Automated trading workflow with scheduling and monitoring.
"""

import os
import sys
import time
import yaml
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from enum import Enum

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)

class WorkflowStep:
    """Single workflow step."""
    def __init__(self, name: str, func: Callable, dependencies: List[str] = None,
                 retry_count: int = 3, timeout: int = 300):
        self.name = name
        self.func = func
        self.dependencies = dependencies or []
        self.retry_count = retry_count
        self.timeout = timeout
        self.status = 'pending'
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
        
class WorkflowEngine:
    """
    Automated workflow engine for trading operations.
    """
    def __init__(self, config_path: str = None):
        self.steps: Dict[str, WorkflowStep] = {}
        self.execution_log: List[Dict] = []
        self.config_path = config_path
        self._load_config()
        
    def _load_config(self):
        """Load workflow configuration."""
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            self._build_workflow_from_config(config)
            
    def _build_workflow_from_config(self, config: Dict):
        """Build workflow from YAML config."""
        for step_name, step_config in config.get('steps', {}).items():
            self.add_step(
                name=step_name,
                func=None,  # Will be set later
                dependencies=step_config.get('dependencies', []),
                retry_count=step_config.get('retry_count', 3),
                timeout=step_config.get('timeout', 300)
            )
            
    def add_step(self, name: str, func: Callable, dependencies: List[str] = None,
                retry_count: int = 3, timeout: int = 300):
        """Add a workflow step."""
        self.steps[name] = WorkflowStep(
            name=name,
            func=func,
            dependencies=dependencies,
            retry_count=retry_count,
            timeout=timeout
        )
        
    def validate_workflow(self) -> bool:
        """Validate workflow for circular dependencies."""
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_name: str) -> bool:
            visited.add(step_name)
            rec_stack.add(step_name)
            
            step = self.steps.get(step_name)
            if step:
                for dep in step.dependencies:
                    if dep not in visited:
                        if has_cycle(dep):
                            return True
                    elif dep in rec_stack:
                        return True
                        
            rec_stack.discard(step_name)
            return False
            
        for step_name in self.steps:
            if step_name not in visited:
                if has_cycle(step_name):
                    return False
        return True
        
    async def execute(self, context: Dict = None) -> Dict:
        """
        Execute the workflow.
        
        Args:
            context: Workflow context/data
            
        Returns:
            Execution results
        """
        if not self.validate_workflow():
            return {'status': 'error', 'message': 'Invalid workflow: circular dependencies'}
            
        context = context or {}
        results = {}
        
        # Execute steps in dependency order
        executed = set()
        pending = list(self.steps.keys())
        
        max_iterations = len(self.steps) * 2
        iteration = 0
        
        while pending and iteration < max_iterations:
            iteration += 1
            ready_steps = []
            
            for step_name in pending:
                step = self.steps[step_name]
                if all(dep in executed for dep in step.dependencies):
                    ready_steps.append(step_name)
                    
            for step_name in ready_steps:
                result = await self._execute_step(step_name, context)
                results[step_name] = result
                executed.add(step_name)
                pending.remove(step_name)
                
        return {
            'status': 'success' if not pending else 'partial',
            'results': results,
            'executed': len(executed),
            'total': len(self.steps)
        }
        
    async def _execute_step(self, step_name: str, context: Dict) -> Dict:
        """Execute a single workflow step."""
        step = self.steps[step_name]
        step.status = 'running'
        step.start_time = datetime.now()
        
        result = {
            'name': step_name,
            'status': 'pending',
            'start_time': step.start_time.isoformat(),
        }
        
        for attempt in range(1, step.retry_count + 1):
            try:
                # Execute with timeout
                import asyncio
                if asyncio.iscoroutinefunction(step.func):
                    step_result = await asyncio.wait_for(
                        step.func(context), timeout=step.timeout
                    )
                else:
                    step_result = step.func(context)
                    
                step.status = 'success'
                step.result = step_result
                result['status'] = 'success'
                result['result'] = step_result
                break
                
            except Exception as e:
                logger.error(f"Step {step_name} attempt {attempt} failed: {e}")
                result['error'] = str(e)
                
                if attempt < step.retry_count:
                    await asyncio.sleep(1)
                    
        step.end_time = datetime.now()
        result['end_time'] = step.end_time.isoformat()
        result['duration'] = (step.end_time - step.start_time).total_seconds()
        
        # Log execution
        self.execution_log.append(result)
        
        return result
        
    def get_status(self) -> Dict:
        """Get workflow status."""
        return {
            'total_steps': len(self.steps),
            'execution_log_count': len(self.execution_log),
            'steps': {
                name: {
                    'status': step.status,
                    'dependencies': step.dependencies
                }
                for name, step in self.steps.items()
            }
        }
        
    def generate_report(self) -> str:
        """Generate workflow report."""
        lines = []
        lines.append("=" * 60)
        lines.append("🔄 工作流执行报告")
        lines.append("=" * 60)
        lines.append(f"\n📊 步骤数: {len(self.steps)}")
        lines.append(f"📋 执行记录: {len(self.execution_log)} 条")
        
        lines.append(f"\n📝 步骤列表")
        for name, step in self.steps.items():
            status_icon = "✅" if step.status == 'success' else "⏳"
            lines.append(f"  {status_icon} {name}")
            if step.dependencies:
                lines.append(f"    依赖: {', '.join(step.dependencies)}")
                
        return "\n".join(lines)


# Global workflow engine
workflow_engine = WorkflowEngine()
