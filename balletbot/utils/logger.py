"""
Logging configuration for BalletBot: Outbreak Dominion
"""

import logging
import os
from pathlib import Path
from config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Setup logging configuration"""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    loggers = [
        'balletbot',
        'bale',
        'PIL'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
    
    # Reduce Bale library logging
    logging.getLogger('bale').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)