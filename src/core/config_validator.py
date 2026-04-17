"""
Core module - Configuration validation with schema.
"""

import os
import sys
import yaml
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

@dataclass
class ConfigField:
    """Configuration field definition."""
    name: str
    field_type: type = str
    required: bool = True
    default: Any = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    choices: Optional[List] = None
    description: str = ""

@dataclass
class ConfigSchema:
    """Configuration schema definition."""
    name: str
    fields: List[ConfigField] = field(default_factory=list)
    
    def add_field(self, field: ConfigField) -> None:
        """Add a field to the schema."""
        self.fields.append(field)

class ConfigValidator:
    """Validates configuration against schemas."""
    
    def __init__(self):
        self.schemas: Dict[str, ConfigSchema] = {}
        self._define_schemas()
        
    def _define_schemas(self) -> None:
        """Define all configuration schemas."""
        # Risk config schema
        risk_schema = ConfigSchema(name="risk")
        risk_schema.add_field(ConfigField("total_capital", float, True, 1000000, 0))
        risk_schema.add_field(ConfigField("max_single_position_pct", float, True, 0.10, 0, 1))
        risk_schema.add_field(ConfigField("stop_loss_pct", float, True, 0.08, 0, 1))
        risk_schema.add_field(ConfigField("take_profit_pct", float, True, 0.20, 0, 1))
        risk_schema.add_field(ConfigField("max_daily_loss_pct", float, True, 0.03, 0, 1))
        risk_schema.add_field(ConfigField("max_drawdown_pct", float, True, 0.15, 0, 1))
        risk_schema.add_field(ConfigField("max_position_count", int, True, 10, 1))
        self.schemas["risk"] = risk_schema
        
        # App config schema
        app_schema = ConfigSchema(name="app")
        app_schema.add_field(ConfigField("name", str, False, "Cuihua Quant"))
        app_schema.add_field(ConfigField("version", str, False, "0.1.0"))
        self.schemas["app"] = app_schema
        
        # Strategies config schema
        strategy_schema = ConfigSchema(name="strategies")
        strategy_schema.add_field(ConfigField("buy_threshold", float, False, 0.5, -1, 1))
        strategy_schema.add_field(ConfigField("sell_threshold", float, False, -0.3, -1, 1))
        self.schemas["strategies"] = strategy_schema
        
    def validate(self, config_name: str, config: Dict) -> List[str]:
        """
        Validate configuration against schema.
        
        Returns:
            List of validation errors (empty if valid)
        """
        if config_name not in self.schemas:
            return [f"Unknown config: {config_name}"]
            
        schema = self.schemas[config_name]
        errors = []
        
        for field_def in schema.fields:
            value = config.get(field_def.name)
            
            # Check required
            if field_def.required and (value is None or value == ""):
                if field_def.default is not None:
                    config[field_def.name] = field_def.default
                else:
                    errors.append(f"Missing required field: {field_def.name}")
                    continue
            elif value is None:
                value = field_def.default
                
            # Check type
            try:
                value = field_def.field_type(value)
            except (ValueError, TypeError):
                errors.append(f"Invalid type for {field_def.name}: expected {field_def.field_type.__name__}")
                continue
                
            # Check range
            if field_def.min_value is not None and value < field_def.min_value:
                errors.append(f"{field_def.name} must be >= {field_def.min_value}")
            if field_def.max_value is not None and value > field_def.max_value:
                errors.append(f"{field_def.name} must be <= {field_def.max_value}")
                
            # Check choices
            if field_def.choices and value not in field_def.choices:
                errors.append(f"{field_def.name} must be one of {field_def.choices}")
                
        return errors
        
    def validate_all(self, config_dir: Optional[str] = None) -> Dict[str, List[str]]:
        """Validate all configuration files."""
        if config_dir is None:
            config_dir = os.path.join(project_root, "config")
            
        results = {}
        
        for filename in ["risk.yaml", "app.yaml", "strategies.yaml"]:
            config_name = filename.replace(".yaml", "")
            filepath = os.path.join(config_dir, filename)
            
            if not os.path.exists(filepath):
                results[config_name] = [f"File not found: {filename}"]
                continue
                
            with open(filepath, "r") as f:
                config = yaml.safe_load(f) or {}
                
            errors = self.validate(config_name, config)
            results[config_name] = errors
            
        return results
        
    def generate_report(self, config_dir: Optional[str] = None) -> str:
        """Generate validation report."""
        results = self.validate_all(config_dir)
        
        lines = []
        lines.append("=" * 50)
        lines.append("⚙️ 配置验证报告")
        lines.append("=" * 50)
        
        all_valid = True
        for config_name, errors in results.items():
            if errors:
                all_valid = False
                lines.append(f"\n❌ {config_name}.yaml")
                for error in errors:
                    lines.append(f"  - {error}")
            else:
                lines.append(f"\n✅ {config_name}.yaml")
                
        lines.append(f"\n{'✅ 所有配置验证通过' if all_valid else '❌ 存在配置错误'}")
        lines.append("=" * 50)
        
        return "\n".join(lines)
