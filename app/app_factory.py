from litestar import Litestar
from litestar.config.cors import CORSConfig

from app.config import config
from app.models import database
from app.routes import routers
from app.logger import logger

def create_app(include_worker: bool = False):
    async def on_startup():
        logger.info("Запуск приложения...")
        await database.connect()

        if include_worker:
            import asyncio
            from app.services.blockchain_worker import blockchain_worker
            asyncio.create_task(blockchain_worker.start())
            logger.info("API и Worker запущены")
        else:
            logger.info("API сервер готов")

    async def on_shutdown():
        if include_worker:
            from app.services.blockchain_worker import blockchain_worker
            blockchain_worker.stop()

        await database.disconnect()
        logger.info("Приложение остановлено")

    cors_config = CORSConfig(
        allow_origins=config.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(f"Настройка CORS: {config.CORS_ORIGINS}")

    app = Litestar(
        route_handlers=routers,
        cors_config=cors_config,
        on_startup=[on_startup],
        on_shutdown=[on_shutdown],
        debug=config.DEBUG,
    )

    return app
