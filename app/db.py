import asyncpg
from typing import Optional, Dict, Any
from .config import config
from .logger import logger

class DB:
    def __init__(self):
        self.connection = None
        self.connected = False
    
    async def connect(self) -> None:
        try:
            self.connection = await asyncpg.connect(config.DATABASE_URL)
            await self.create_tables()
            self.connected = True
            logger.info("База данных подключена")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    async def disconnect(self) -> None:
        if self.connection:
            await self.connection.close()
            self.connected = False
    
    async def create_tables(self) -> None:
        create_sql = """
            CREATE TABLE IF NOT EXISTS document_records (
                id SERIAL PRIMARY KEY,
                verification_id VARCHAR(64) UNIQUE NOT NULL,
                document_hash VARCHAR(128) UNIQUE NOT NULL,
                creator_address VARCHAR(42) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                block_number INTEGER NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_verification_id ON document_records(verification_id);
            CREATE INDEX IF NOT EXISTS idx_document_hash ON document_records(document_hash);
            CREATE INDEX IF NOT EXISTS idx_creator_address ON document_records(creator_address);
            CREATE INDEX IF NOT EXISTS idx_block_number ON document_records(block_number);
        """
        await self.connection.execute(create_sql)
    
    async def insert_document(self, verification_id: str, document_hash: str,
                             creator_address: str, block_number: int) -> None:
        try:
            await self.connection.execute(
                """INSERT INTO document_records
                   (verification_id, document_hash, creator_address, block_number)
                   VALUES ($1, $2, $3, $4) ON CONFLICT (verification_id) DO NOTHING""",
                verification_id, document_hash, creator_address, block_number
            )
        except Exception as e:
            logger.error(f"Ошибка вставки документа: {e}")
    
    async def get_by_verification_id(self, verification_id: str) -> Optional[Dict[str, Any]]:
        try:
            record = await self.connection.fetchrow(
                "SELECT * FROM document_records WHERE verification_id = $1",
                verification_id
            )
            return dict(record) if record else None
        except Exception as e:
            logger.error(f"Ошибка получения документа по ID: {e}")
            return None
    
    async def get_by_document_hash(self, document_hash: str) -> Optional[Dict[str, Any]]:
        try:
            record = await self.connection.fetchrow(
                "SELECT * FROM document_records WHERE document_hash = $1",
                document_hash
            )
            return dict(record) if record else None
        except Exception as e:
            logger.error(f"Ошибка получения документа по хешу: {e}")
            return None
    
    async def hash_exists(self, document_hash: str) -> bool:
        try:
            return await self.connection.fetchval(
                "SELECT EXISTS(SELECT 1 FROM document_records WHERE document_hash = $1)",
                document_hash
            )
        except Exception as e:
            logger.error(f"Ошибка проверки существования хеша: {e}")
            return False

# Singleton instance
db = DB()