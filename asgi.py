from app.app_factory import app_factory
from app.config import config
from app.logger import logger

class ASGIApplication:
    def __init__(self):
        self.app_factory = app_factory
        self.config = config
        self.logger = logger
        
        # Set log level from config
        self.logger.set_level(self.config.LOG_LEVEL)
        
        # Create application without worker for ASGI servers
        self.app = self.app_factory.create_app(include_worker=False)
    
    def get_app(self):
        return self.app

# Create ASGI application
asgi_app = ASGIApplication()
app = asgi_app.get_app()