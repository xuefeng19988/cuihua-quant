"""
Phase 20.3: Audit log for trading operations.
"""

import os
import sys
import json
import csv
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

@dataclass
class AuditEntry:
    """Audit log entry."""
    timestamp: str
    user: str
    action: str
    resource: str
    details: Dict
    ip_address: str = ""
    result: str = "SUCCESS"

class AuditLogger:
    """
    Audit logging for compliance and security.
    Records all trading operations and system changes.
    """
    
    def __init__(self, log_dir: Optional[str] = None):
        if log_dir is None:
            log_dir = os.path.join(project_root, "data", "audit")
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        self.entries: List[AuditEntry] = []
        
    def log(
        self,
        action: str,
        resource: str,
        details: Dict,
        user: str = "system",
        ip_address: str = "",
        result: str = "SUCCESS",
    ) -> None:
        """
        Record an audit entry.
        
        Args:
            action: Action performed (e.g., "ORDER_SUBMIT", "CONFIG_CHANGE")
            resource: Resource affected (e.g., stock code, config file)
            details: Additional details
            user: User who performed the action
            ip_address: Source IP address
            result: Result of the action
        """
        entry = AuditEntry(
            timestamp=datetime.now().isoformat(),
            user=user,
            action=action,
            resource=resource,
            details=details,
            ip_address=ip_address,
            result=result,
        )
        self.entries.append(entry)
        self._write_entry(entry)
        
    def _write_entry(self, entry: AuditEntry) -> None:
        """Write entry to daily log file."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(self.log_dir, f"audit_{date_str}.jsonl")
        
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")
            
    def query(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        user: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
    ) -> List[AuditEntry]:
        """Query audit logs."""
        results = list(self.entries)
        
        # Load from files if needed
        if start_date:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            results = [e for e in results if datetime.fromisoformat(e.timestamp) >= start]
            
        if end_date:
            end = datetime.strptime(end_date, "%Y-%m-%d")
            results = [e for e in results if datetime.fromisoformat(e.timestamp) <= end]
            
        if user:
            results = [e for e in results if e.user == user]
        if action:
            results = [e for e in results if e.action == action]
        if result:
            results = [e for e in results if e.result == result]
            
        return results
        
    def export_csv(self, filepath: str, entries: Optional[List[AuditEntry]] = None) -> None:
        """Export audit logs to CSV."""
        if entries is None:
            entries = self.entries
            
        if not entries:
            return
            
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=AuditEntry.__dataclass_fields__.keys())
            writer.writeheader()
            for entry in entries:
                writer.writerow(asdict(entry))
                
    def generate_report(self, days: int = 7) -> str:
        """Generate audit report."""
        entries = self.query()
        
        lines = []
        lines.append("=" * 60)
        lines.append("🔒 审计日志报告")
        lines.append("=" * 60)
        
        # Summary
        lines.append(f"\n📊 统计 (最近 {days} 天)")
        lines.append(f"  总记录数: {len(entries)}")
        
        # By action
        action_counts = {}
        for entry in entries:
            action_counts[entry.action] = action_counts.get(entry.action, 0) + 1
            
        lines.append(f"\n📋 操作分布")
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  {action}: {count}")
            
        # Recent entries
        lines.append(f"\n📝 最近 10 条记录")
        for entry in entries[-10:]:
            icon = "✅" if entry.result == "SUCCESS" else "❌"
            lines.append(f"  {icon} {entry.timestamp[:16]} | {entry.user} | {entry.action} | {entry.resource}")
            
        return "\n".join(lines)


# Global audit logger instance
audit_logger = AuditLogger()
