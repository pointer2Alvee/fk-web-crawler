import logging
import os
logging.getLogger("pymongo").setLevel(logging.WARNING) # prevents all unnecessary debug logs when cralwer/scheduler run
# Cache loggers to prevent duplicate setup
_loggers = {}  

def setup_logger(name="crawler_logger", log_file="logs/activity.log"):
    """
    Create or reuse a logger instance with a file handler only once.
    """
    if name in _loggers:
        return _loggers[name]

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Add only if not already added
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(log_file) for h in logger.handlers):
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False  

    # Cache it
    _loggers[name] = logger 
    
    return logger
