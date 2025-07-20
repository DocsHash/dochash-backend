from sqlalchemy import Column, String, DateTime, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import asyncpg
from app.config import config
from app.logger import logger

Base = declarative_base()

class DocumentRecord(Base):
    __tablename__ = "document_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_id = Column(String(64), unique=True, nullable=False, index=True)
    document_hash = Column(String(128), unique=True, nullable=False, index=True)
    creator_address = Column(String(42), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    block_number = Column(Integer, nullable=False, index=True)

    __table_args__ = (
        Index('idx_verification_id', 'verification_id'),
        Index('idx_document_hash', 'document_hash'),
        Index('idx_creator_address', 'creator_address'),
        Index('idx_block_number', 'block_number'),
    )

class Database:
    def __init__(self):
        self.connection = None

    async def connect(self):
        try:
            self.connection = await asyncpg.connect(config.DATABASE_URL)
            await self.create_tables()
            logger.info("База данных подключена")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    async def disconnect(self):
        if self.connection:
            await self.connection.close()

    async def create_tables(self):
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
                              creator_address: str, block_number: int):
        try:
            await self.connection.execute(
                """INSERT INTO document_records
                   (verification_id, document_hash, creator_address, block_number)
                   VALUES ($1, $2, $3, $4) ON CONFLICT (verification_id) DO NOTHING""",
                verification_id, document_hash, creator_address, block_number
            )
        except Exception as e:
            logger.error(f"Ошибка вставки документа: {e}")

    async def get_by_verification_id(self, verification_id: str):
        return await self.connection.fetchrow(
            "SELECT * FROM document_records WHERE verification_id = $1",
            verification_id
        )

    async def get_by_document_hash(self, document_hash: str):
        return await self.connection.fetchrow(
            "SELECT * FROM document_records WHERE document_hash = $1",
            document_hash
        )

    async def hash_exists(self, document_hash: str) -> bool:
        return await self.connection.fetchval(
            "SELECT EXISTS(SELECT 1 FROM document_records WHERE document_hash = $1)",
            document_hash
        )

database = Database()
