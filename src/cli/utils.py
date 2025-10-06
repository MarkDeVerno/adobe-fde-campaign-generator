"""
CLI utility functions for formatting and logging.
"""
from typing import Optional
import sys
import structlog


# ANSI color codes
COLORS = {
    'success': '\033[92m',  # Green
    'error': '\033[91m',    # Red
    'warning': '\033[93m',  # Yellow
    'info': '\033[94m',     # Blue
    'header': '\033[95m',   # Magenta
    'reset': '\033[0m'
}


def print_success(message: str):
    """Print success message in green."""
    print(f"{COLORS['success']}✅ {message}{COLORS['reset']}")


def print_error(message: str):
    """Print error message in red."""
    print(f"{COLORS['error']}❌ {message}{COLORS['reset']}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message in yellow."""
    print(f"{COLORS['warning']}⚠️  {message}{COLORS['reset']}")


def print_info(message: str):
    """Print info message in blue."""
    print(f"{COLORS['info']}ℹ️  {message}{COLORS['reset']}")


def print_header(message: str):
    """Print header message in magenta."""
    print(f"\n{COLORS['header']}{'=' * 60}{COLORS['reset']}")
    print(f"{COLORS['header']}{message}{COLORS['reset']}")
    print(f"{COLORS['header']}{'=' * 60}{COLORS['reset']}\n")


def setup_logging(verbose: bool = False):
    """
    Configure structured logging.

    Args:
        verbose: If True, enable DEBUG level logging
    """
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if verbose:
        print_info("Verbose logging enabled")
