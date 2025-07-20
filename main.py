import asyncio
import uvicorn
from app.app_factory import app_factory
from app.config import config
from app.logger import logger

class ApplicationServer:
    def __init__(self):
        self.app_factory = app_factory
        self.config = config
        self.logger = logger
    
    async def run(self):
        """Run the application server"""
        # Set log level from config
        self.logger.set_level(self.config.LOG_LEVEL)
        
        # Create application with worker
        self.logger.info("Инициализация сервера...")
        app = self.app_factory.create_app(include_worker=True)
        
        # Configure uvicorn server
        server_config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8000,
            reload=self.config.DEBUG,
            log_level=self.config.LOG_LEVEL.lower()
        )
        
        # Start server
        self.logger.info(f"Запуск сервера: host=0.0.0.0, port=8000, debug={self.config.DEBUG}")
        server = uvicorn.Server(server_config)
        await server.serve()

# Run the server
if __name__ == "__main__":
    server = ApplicationServer()
    asyncio.run(server.run())