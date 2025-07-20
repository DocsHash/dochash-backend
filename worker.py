import asyncio
from app.models import database
from app.services.blockchain_worker import blockchain_worker
from app.logger import logger

async def run_worker():
    logger.info("Запуск Blockchain Worker...")
    await database.connect()

    try:
        await blockchain_worker.start()
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки")
    finally:
        blockchain_worker.stop()
        await database.disconnect()
        logger.info("Blockchain Worker остановлен")

if __name__ == "__main__":
    asyncio.run(run_worker())
