"""
Logging configuration for the application.
"""
import logging
import sys
from pathlib import Path
from config import config


def setup_logger(name: str = None) -> logging.Logger:
    """
    Set up application logger.

    Args:
        name: Logger name (usually __name__ of the module)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name or 'market_analysis')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    console_handler.setFormatter(simple_formatter)

    # File handler
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_dir / 'app.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(detailed_formatter)

    # Error file handler
    error_handler = logging.FileHandler(log_dir / 'error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


# Create default logger
default_logger = setup_logger()
