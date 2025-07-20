import asyncio
from app.db import db
from app.blockchain import blockchain
from app.logger import logger
from app.config import config

class BlockchainWorkerRunner:
    def __init__(self):
        self.db = db
        self.blockchain = blockchain
        self.logger = logger
        self.config = config
    
    async def run(self):
        """Run standalone blockchain worker"""
        # Set log level from config
        self.logger.set_level(self.config.LOG_LEVEL)
        
        # Start worker
        self.logger.info("Запуск Blockchain Worker...")
        await self.db.connect()
        
        try:
            await self.blockchain.start_worker()
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал остановки")
        finally:
            self.blockchain.stop_worker()
            await self.db.disconnect()
            self.logger.info("Blockchain Worker остановлен")

# Run the worker
if __name__ == "__main__":
    worker_runner = BlockchainWorkerRunner()
    asyncio.run(worker_runner.run())