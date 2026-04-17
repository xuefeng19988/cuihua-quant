"""
Phase 19.1: Enhanced CLI with progress bars and colors.
"""

import os
import sys
import time
import yaml
from typing import List, Optional, Callable
from datetime import datetime

# Project paths
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

class Colors:
    """ANSI color codes for terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BG_BLUE = "\033[44m"
    BG_GREEN = "\033[42m"
    BG_RED = "\033[41m"

class ProgressBar:
    """Simple text-based progress bar."""
    
    def __init__(self, total: int, prefix: str = "", width: int = 40):
        self.total = total
        self.prefix = prefix
        self.width = width
        self.current = 0
        
    def update(self, n: int = 1) -> None:
        """Update progress bar."""
        self.current += n
        self._render()
        
    def _render(self) -> None:
        """Render progress bar."""
        if self.total == 0:
            return
        pct = self.current / self.total
        filled = int(self.width * pct)
        bar = "█" * filled + "░" * (self.width - filled)
        print(f"\r{self.prefix} |{bar}| {self.current}/{self.total} ({pct:.0%})", end="", flush=True)
        
    def complete(self, message: str = "Done") -> None:
        """Complete progress bar."""
        self._render()
        print(f" {Colors.GREEN}✓{Colors.RESET} {message}")

def print_header(title: str, width: int = 60) -> None:
    """Print colored header."""
    print(f"\n{Colors.BOLD}{Colors.BG_BLUE}{' ' * width}")
    print(f"  {title.center(width - 4)}")
    print(f"{' ' * width}{Colors.RESET}\n")

def print_section(title: str) -> None:
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'─' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}{title}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 50}{Colors.RESET}")

def print_success(message: str) -> None:
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")

def print_error(message: str) -> None:
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")

def print_warning(message: str) -> None:
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")

def print_info(message: str) -> None:
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")

def print_table(headers: List[str], rows: List[List[str]], col_widths: Optional[List[int]] = None) -> None:
    """Print formatted table."""
    if not col_widths:
        col_widths = [max(len(str(item)) for item in col) for col in zip(headers, *rows)]
        
    # Header
    header_line = "  ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(f"{Colors.BOLD}{Colors.UNDERLINE}{header_line}{Colors.RESET}")
    
    # Rows
    for row in rows:
        line = "  ".join(f"{str(item):<{w}}" for item, w in zip(row, col_widths))
        print(line)

def run_with_progress(func: Callable, items: List, desc: str = "Processing") -> List:
    """Run function with progress bar."""
    bar = ProgressBar(len(items), desc)
    results = []
    for item in items:
        result = func(item)
        results.append(result)
        bar.update()
    bar.complete()
    return results
