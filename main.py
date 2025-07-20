import asyncio
import uvicorn
from app.app_factory import create_app
from app.config import config
from app.logger import logger

async def run_server():
    logger.info("Инициализация сервера...")
    app = create_app(include_worker=True)

    server_config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8000,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
    
    logger.info(f"Настройка сервера: host=0.0.0.0, port=8000, debug={config.DEBUG}")
    server = uvicorn.Server(server_config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(run_server())
