import logging
import os
logging.getLogger("pymongo").setLevel(logging.WARNING) # prevents all unnecessary debug logs when cralwer/scheduler run
# Cache loggers to prevent duplicate setup
_loggers = {}  

def setup_logger(name="crawler_logger", log_file=None):
    """
    Create or reuse a logger instance with a file handler only once.
    """
    if name in _loggers:
        return _loggers[name]

     # If log_file is not passed, set default relative to this file
    if log_file is None:
        current_dir = os.path.dirname(__file__)
        log_file = os.path.join(current_dir, "logs", "activity.log")
        
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
