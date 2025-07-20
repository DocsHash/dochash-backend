import asyncio
from litestar import Litestar
from litestar.config.cors import CORSConfig

from .config import config
from .db import db
from .routes import routers
from .logger import logger
from .blockchain import blockchain

class AppFactory:
    def __init__(self):
        self.db = db
        self.blockchain = blockchain
    
    async def startup(self):
        """Application startup handler"""
        logger.info("Запуск приложения...")
        await self.db.connect()
    
    async def shutdown(self):
        """Application shutdown handler"""
        await self.db.disconnect()
        logger.info("Приложение остановлено")
    
    async def start_worker(self):
        """Start blockchain worker in background task"""
        await self.blockchain.start_worker()
    
    def stop_worker(self):
        """Stop blockchain worker"""
        self.blockchain.stop_worker()
    
    def create_app(self, include_worker: bool = False):
        """Create and configure Litestar application"""
        # Configure CORS
        cors_config = CORSConfig(
            allow_origins=config.CORS_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Define startup handler
        async def on_startup():
            await self.startup()
            if include_worker:
                asyncio.create_task(self.start_worker())
                logger.info("API и Worker запущены")
            else:
                logger.info("API сервер готов")
        
        # Define shutdown handler
        async def on_shutdown():
            if include_worker:
                self.stop_worker()
            await self.shutdown()
        
        # Create application
        app = Litestar(
            route_handlers=routers,
            cors_config=cors_config,
            on_startup=[on_startup],
            on_shutdown=[on_shutdown],
            debug=config.DEBUG,
        )
        
        return app

# Singleton instance
app_factory = AppFactory()