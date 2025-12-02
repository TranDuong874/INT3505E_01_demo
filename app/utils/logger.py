import logging
import sys
from pythonjsonlogger import jsonlogger


# Global flag to prevent duplicate setup
_logging_configured = False


def setup_logging(app_name="books-api", log_level=logging.INFO):
    """
    Configure structured JSON logging for the application
    
    Creates two handlers:
    1. Console handler - outputs to stdout
    2. File handler - writes to logs/app.log with rotation
    """
    global _logging_configured
    
    if _logging_configured:
        return logging.getLogger()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # JSON formatter with custom fields
    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            log_record['timestamp'] = record.created
            log_record['level'] = record.levelname
            log_record['logger'] = record.name
            log_record['module'] = record.module
            log_record['function'] = record.funcName
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(logger)s %(module)s %(function)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # File handler
    try:
        import os
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")
    
    # Add handlers to root logger
    root_logger.addHandler(console_handler)
    
    _logging_configured = True
    
    return root_logger


def get_logger(name=None):
    """Get logger instance - uses root logger configuration"""
    return logging.getLogger(name)

# Your code:
#   logger.info("Books retrieved", extra={"count": 5})
#        ↓
# Python creates:
#   LogRecord(name=..., msg=..., count=5, created=..., func=...)
#        ↓
# Handler calls:
#   CustomJsonFormatter.format(record)
#        ↓
# CustomJsonFormatter calls:
#   add_fields(log_record={}, record=LogRecord)
#        ↓
# You populate:
#   log_record['timestamp'] = record.created
#   log_record['level'] = record.levelname
#   ...
#        ↓
# JsonFormatter calls:
#   json.dumps(log_record)
#        ↓
# Output:
#   {"timestamp": ..., "level": "INFO", ...}