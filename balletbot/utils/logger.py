"""
Logging utilities for BalletBot: Outbreak Dominion
"""

import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """Set up logging configuration"""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/balletbot.log"),
        ]
    )
    
    # Set specific loggers
    logging.getLogger("bale").setLevel(logging.WARNING)  # Reduce Bale API noise
    logging.getLogger("PIL").setLevel(logging.WARNING)   # Reduce Pillow noise

def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)