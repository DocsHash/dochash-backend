import asyncio
import os
from typing import Any
from .blockchain_service import blockchain_service
from ..models import database
from ..config import config
from ..logger import logger

class BlockchainWorker:
    def __init__(self):
        self.running = False
        self.last_block_file = config.LAST_BLOCK_FILE
        self.scan_interval = 10
        self.blockchain = blockchain_service
        self.db = database
        logger.info("BlockchainWorker initialized")

    def get_last_processed_block(self) -> int:
        try:
            if os.path.exists(self.last_block_file):
                with open(self.last_block_file, 'r') as f:
                    block = int(f.read().strip())
                    logger.info(f"Последний обработанный блок: {block}")
                    return block
            default_block = self.blockchain.get_latest_block_number() - 100
            logger.info(f"Файл последнего блока не найден, используем: {default_block}")
            return default_block
        except Exception as e:
            default_block = self.blockchain.get_latest_block_number() - 100
            logger.error(f"Ошибка чтения последнего блока: {e}, используем: {default_block}")
            return default_block

    def save_last_processed_block(self, block_number: int):
        try:
            os.makedirs(os.path.dirname(self.last_block_file), exist_ok=True)
            with open(self.last_block_file, 'w') as f:
                f.write(str(block_number))
            logger.info(f"Сохранен последний обработанный блок: {block_number}")
        except Exception as e:
            logger.error(f"Ошибка сохранения последнего блока: {e}")

    async def process_new_events(self):
        last_block = self.get_last_processed_block()
        current_block = self.blockchain.get_latest_block_number()

        if current_block <= last_block:
            logger.debug(f"Нет новых блоков для обработки: {last_block} >= {current_block}")
            return

        logger.info(f"Сканирование блоков {last_block + 1} - {current_block}")

        try:
            events = self.blockchain.get_document_stored_events(
                from_block=last_block + 1,
                to_block=current_block
            )

            for event in events:
                await self.process_document_event(event)

            self.save_last_processed_block(current_block)

            if events:
                logger.info(f"Обработано {len(events)} событий")

        except Exception as e:
            logger.error(f"Ошибка обработки событий: {e}")

    async def process_document_event(self, event: Any):
        try:
            creator = event.args.creator
            block_number = event.blockNumber
            tx_hash = event.transactionHash.hex()

            logger.info(f"Обработка события из блока {block_number}, tx: {tx_hash}")
            logger.info(f"Создатель: {creator}")

            try:
                doc_count = await self.blockchain.get_creator_document_count(creator)
                logger.info(f"У создателя {doc_count} документов")

                docs = await self.blockchain.get_documents_by_creator(creator)
                if docs:
                    last_verification_id = docs[-1]
                    logger.info(f"Последний verification_id: {last_verification_id}")

                    doc_info = await self.blockchain.get_document_info_by_id(last_verification_id)
                    if doc_info:
                        document_hash, creator_from_contract, timestamp = doc_info
                        logger.info(f"Хеш документа: {document_hash[:10]}...")

                        await self.db.insert_document(
                            verification_id=last_verification_id,
                            document_hash=document_hash,
                            creator_address=creator,
                            block_number=block_number
                        )

                        logger.info(f"Сохранен документ: {last_verification_id}")
                    else:
                        logger.warning("Не удалось получить информацию о документе")
                else:
                    logger.warning("Нет документов для создателя")

            except Exception as e:
                logger.error(f"Ошибка получения документов создателя: {e}")

        except Exception as e:
            logger.error(f"Ошибка обработки события: {e}")

    async def start(self):
        if not self.blockchain.is_connected():
            logger.error("Блокчейн не подключен, воркер не запущен")
            return

        self.running = True
        logger.info("Blockchain worker запущен")

        while self.running:
            try:
                await self.process_new_events()
                await asyncio.sleep(self.scan_interval)
            except Exception as e:
                logger.error(f"Ошибка в воркере: {e}")
                await asyncio.sleep(self.scan_interval)

    def stop(self):
        self.running = False
        logger.info("Blockchain worker остановлен")

blockchain_worker = BlockchainWorker()