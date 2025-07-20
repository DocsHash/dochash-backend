import logging
import sys
from typing import Optional

class Logger:
    DEFAULT_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    def __init__(self, name: str = "dochash", 
                level: Optional[str] = None, 
                format_str: Optional[str] = None):
        self.logger = logging.getLogger(name)
        
        # Set level if provided
        if level:
            self.set_level(level)
        
        # Add handler if not already configured
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(format_str or self.DEFAULT_FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def set_level(self, level: str) -> None:
        self.logger.setLevel(getattr(logging, level))
    
    def debug(self, message: str) -> None:
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        self.logger.critical(message)

# Singleton instance
logger = Logger()