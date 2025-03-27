import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure the logger
def setup_logger():
    """Configure and return the game logger."""
    logger = logging.getLogger('SpaceShooter')
    logger.setLevel(logging.DEBUG)

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler (rotating log files)
    log_file = os.path.join('logs', f'game_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Create the logger instance
logger = setup_logger()

def log_error(error, context=""):
    """Log an error with optional context."""
    logger.error(f"{context} - {str(error)}", exc_info=True)

def log_warning(message):
    """Log a warning message."""
    logger.warning(message)

def log_info(message):
    """Log an info message."""
    logger.info(message)

def log_debug(message):
    """Log a debug message."""
    logger.debug(message)

def log_game_event(event_type, details):
    """Log a game event with specific details."""
    logger.info(f"Game Event - {event_type}: {details}")

def log_performance(operation, time_taken):
    """Log performance metrics."""
    logger.debug(f"Performance - {operation}: {time_taken:.4f}s") 