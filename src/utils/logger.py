import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logger(
    name: str = "agentaru",
    level: str = "INFO",
    log_file: str = None,
    log_dir: str = "logs",
) -> logging.Logger:
    """Setup application logger with file and console handlers"""

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file or log_dir:
        log_dir_path = Path(log_dir)
        log_dir_path.mkdir(parents=True, exist_ok=True)

        if not log_file:
            log_file = f"agentaru_{datetime.now().strftime('%Y%m%d')}.log"

        file_handler = logging.FileHandler(log_dir_path / log_file)
        file_handler.setLevel(logging.DEBUG)  # Log everything to file
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
