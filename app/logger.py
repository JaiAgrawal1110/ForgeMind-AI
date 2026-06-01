# ============================================================
# logger.py — Sets up logging for the entire app
# Instead of print(), we use logger.info() / logger.error()
# This writes logs with timestamps to console AND a file
# ============================================================

from loguru import logger
import sys

def setup_logger():
    # Remove the default loguru handler
    logger.remove()

    # Log to console (terminal) with colors
    logger.add(
        sys.stdout,
        level="INFO",                          # Show INFO and above (INFO, WARNING, ERROR)
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level}</level> | "
               "<cyan>{name}</cyan> - <level>{message}</level>"
    )

    # Also log to a file inside the /logs folder
    logger.add(
        "logs/app.log",
        level="DEBUG",                         # File gets everything including DEBUG
        rotation="10 MB",                      # Start a new file after 10MB
        retention="7 days",                    # Delete logs older than 7 days
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} - {message}"
    )

    return logger

# Create one logger instance — import this everywhere
log = setup_logger()
