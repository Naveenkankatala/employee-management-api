import logging
import os
from logging.handlers import RotatingFileHandler

# Create logs folder
log_directory = "logs"
os.makedirs(log_directory, exist_ok=True)

log_file = os.path.join(log_directory, "app.log")


# File handler
# delay=True means app.log is created only
# when the first log message is written
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    delay=True
)


# Log format
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)

file_handler.setFormatter(formatter)


# Application logger
logger = logging.getLogger("employee_management")

logger.setLevel(logging.INFO)

# Prevent duplicate logs
logger.propagate = False

# Avoid adding the handler multiple times
if not logger.handlers:
    logger.addHandler(file_handler)