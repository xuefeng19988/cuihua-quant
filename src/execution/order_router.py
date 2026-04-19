"""
Phase 38: Smart Order Router
Intelligent order routing with best execution.
"""

import os
import sys
import time
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class SmartOrderRouter:
    """
    Smart order routing for best execution.
    """
    
    def __init__(self):
        self.brokers = {}
        self.execution_log: List[Dict] = []
        
    def register_broker(self, broker_id: str, broker: object):
        """Register a broker for order routing."""
        self.brokers[broker_id] = broker
        
    def route_order(self, order: Dict) -> Dict:
        """
        Route order to best broker.
        
        Args:
            order: Order dict with code, action, shares, price
            
        Returns:
            Execution result
        """
        if not self.brokers:
            return {'status': 'error', 'message': 'No brokers registered'}
            
        # Select best broker based on:
        # 1. Lowest commission
        # 2. Fastest execution
        # 3. Best fill rate
        
        best_broker = None
        best_score = float('inf')
        
        for broker_id, broker in self.brokers.items():
            score = self._calculate_broker_score(broker, order)
            if score < best_score:
                best_score = score
                best_broker = broker_id
                
        if best_broker:
            return self._execute_order(best_broker, order)
            
        return {'status': 'error', 'message': 'No suitable broker found'}
        
    def _calculate_broker_score(self, broker: object, order: Dict) -> float:
        """Calculate broker score (lower is better)."""
        # Simple scoring: commission + latency penalty
        commission = getattr(broker, 'commission_rate', 0.001)
        latency = getattr(broker, 'avg_latency_ms', 100)
        
        return commission + (latency / 10000)  # Normalize latency
        
    def _execute_order(self, broker_id: str, order: Dict) -> Dict:
        """Execute order through selected broker."""
        broker = self.brokers[broker_id]
        
        # Execute
        try:
            if hasattr(broker, 'place_order'):
                result = broker.place_order(order)
            else:
                result = {'status': 'error', 'message': 'Broker does not support place_order'}
        except Exception as e:
            result = {'status': 'error', 'message': str(e)}
            
        # Log
        self.execution_log.append({
            'broker': broker_id,
            'order': order,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
        
    def get_execution_stats(self) -> Dict:
        """Get execution statistics."""
        if not self.execution_log:
            return {'total_orders': 0}
            
        successful = sum(1 for log in self.execution_log if log['result'].get('status') == 'success')
        
        broker_stats = {}
        for log in self.execution_log:
            broker = log['broker']
            if broker not in broker_stats:
                broker_stats[broker] = {'total': 0, 'success': 0}
            broker_stats[broker]['total'] += 1
            if log['result'].get('status') == 'success':
                broker_stats[broker]['success'] += 1
                
        return {
            'total_orders': len(self.execution_log),
            'successful_orders': successful,
            'success_rate': successful / len(self.execution_log) if self.execution_log else 0,
            'broker_stats': broker_stats
        }
