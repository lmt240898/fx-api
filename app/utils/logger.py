# filepath: c:\GIT\BotT\v4\utils\logger.py
import os
import logging
from datetime import datetime
import sys
from logging.handlers import TimedRotatingFileHandler

class Logger:
    _loggers = {}

    def __new__(cls, name, custom_log_path=None):
        if name in cls._loggers and not custom_log_path:
            return cls._loggers[name]
        
        logger = super(Logger, cls).__new__(cls)
        cls._loggers[name] = logger
        return logger

    def __init__(self, name, custom_log_path=None):
        # Avoid re-initialization if the logger already exists (standard singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.name = name
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(logging.DEBUG)
        
        self._setup_logger(custom_log_path)
        self._initialized = True

    def _setup_logger(self, custom_log_path=None):
        # Prevent adding handlers multiple times
        if self.logger.hasHandlers():
            return
            
        if custom_log_path:
            # --- NEW LOGIC: Use a custom, full file path ---
            log_dir = os.path.dirname(custom_log_path)
            log_file_path = custom_log_path
        else:
            # --- OLD LOGIC (Fallback): Standard date-based directory structure ---
            now = datetime.now()
            log_dir = f"logs/{now.strftime('%m-%Y')}/{now.strftime('%d')}/{self.name}"
            log_file_path = f"{log_dir}/{now.strftime('%d%m%y')}.log"

        # Create directory if it doesn't exist for both cases
        os.makedirs(log_dir, exist_ok=True)
        
        # --- Handler Configuration (remains the same) ---
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler (use the determined path)
        file_handler = logging.FileHandler(log_file_path, 'a', 'utf-8')
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _ensure_logger(self):
        """Ensure logger is initialized"""
        if not self._initialized:
            self._setup_logger()
    
    def debug(self, message):
        """Log a debug message"""
        try:
            self._ensure_logger()
            self.logger.debug(message)
        except Exception as e:
            print(f"Error logging debug message: {e}")
    
    def info(self, message):
        """Log an info message"""
        try:
            self._ensure_logger()
            # Ensure message is properly encoded if it's not already a string
            if not isinstance(message, str):
                message = str(message)
            self.logger.info(message)
        except Exception as e:
            print(f"Error logging info message: {e}")
            # As a fallback, print to console
            print(f"LOG INFO: {message[:200]}... (truncated)")
    
    def warning(self, message, exc_info=False):
        """Log a warning message, optionally with exception info"""
        try:
            self._ensure_logger()
            self.logger.warning(message, exc_info=exc_info)
        except Exception as e:
            print(f"Error logging warning message: {e}")
    
    def error(self, message, exc_info=False):
        """Log an error message, optionally with exception info"""
        try:
            self._ensure_logger()
            self.logger.error(message, exc_info=exc_info)
        except Exception as e:
            print(f"Error logging error message: {e}")

    def critical(self, message, exc_info=False):
        """Log a critical message, optionally with exception info"""
        try:
            self._ensure_logger()
            self.logger.critical(message, exc_info=exc_info)
        except Exception as e:
            print(f"Error logging critical message: {e}")

    def set_database_logging(self, enabled: bool):
        """Enable or disable database logging"""
        self.enable_database_logging = enabled
        # Re-setup logger with new database logging setting
        self._initialized = False
        self._setup_logger()
        self.info(f"Database logging {'enabled' if enabled else 'disabled'} for {self.feature_folder}")
