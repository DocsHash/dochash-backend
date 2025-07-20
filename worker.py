import asyncio
from app.models import database
from app.services.blockchain_worker import blockchain_worker


async def run_worker():
    print("🔧 Запуск Blockchain Worker...")
    await database.connect()

    try:
        await blockchain_worker.start()
    except KeyboardInterrupt:
        print("🛑 Получен сигнал остановки")
    finally:
        blockchain_worker.stop()
        await database.disconnect()
        print("✅ Blockchain Worker остановлен")


if __name__ == "__main__":
    asyncio.run(run_worker())
