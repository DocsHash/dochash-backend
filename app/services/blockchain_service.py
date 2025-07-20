from web3 import Web3
from typing import Optional, Tuple, List
from ..config import config
from ..logger import logger

class BlockchainService:
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        self.contract = self.w3.eth.contract(
            address=config.CONTRACT_ADDRESS,
            abi=config.CONTRACT_ABI
        )
        logger.info(f"Blockchain service initialized with RPC: {config.RPC_URL}")

    def is_connected(self) -> bool:
        try:
            connected = self.w3.is_connected()
            if connected:
                logger.info("Blockchain connection established")
            else:
                logger.warning("Blockchain connection failed")
            return connected
        except Exception as e:
            logger.error(f"Ошибка проверки подключения к блокчейну: {e}")
            return False

    async def check_hash_exists(self, document_hash: str) -> bool:
        try:
            result = self.contract.functions.hashExists(document_hash).call()
            logger.info(f"Проверка хеша {document_hash[:10]}...: {'существует' if result else 'не существует'}")
            return result
        except Exception as e:
            logger.error(f"Ошибка проверки хеша в блокчейне: {e}")
            return False

    async def get_document_info_by_id(self, verification_id: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfo(verification_id).call()
            if result[0]:
                logger.info(f"Получена информация о документе по ID: {verification_id}")
                return result[0], result[1], result[2]
            logger.info(f"Документ с ID {verification_id} не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения документа по ID: {e}")
            return None

    async def get_document_info_by_hash(self, document_hash: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfoByHash(document_hash).call()
            if result[0]:
                logger.info(f"Получена информация о документе по хешу: {document_hash[:10]}...")
                return result[0], result[1], result[2]
            logger.info(f"Документ с хешем {document_hash[:10]}... не найден")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения документа по хешу: {e}")
            return None

    async def get_creator_document_count(self, creator_address: str) -> int:
        try:
            count = self.contract.functions.getCreatorDocumentCount(creator_address).call()
            logger.info(f"Количество документов создателя {creator_address[:10]}...: {count}")
            return count
        except Exception as e:
            logger.error(f"Ошибка получения количества документов: {e}")
            return 0

    async def get_documents_by_creator(self, creator_address: str) -> List[str]:
        try:
            docs = self.contract.functions.getDocumentsByCreator(creator_address).call()
            logger.info(f"Получено {len(docs)} документов создателя {creator_address[:10]}...")
            return docs
        except Exception as e:
            logger.error(f"Ошибка получения документов создателя: {e}")
            return []

    def get_latest_block_number(self) -> int:
        try:
            block_number = self.w3.eth.block_number
            logger.debug(f"Текущий номер блока: {block_number}")
            return block_number
        except Exception as e:
            logger.error(f"Ошибка получения номера блока: {e}")
            return 0

    def get_document_stored_events(self, from_block: int, to_block: int = None):
        try:
            if to_block is None:
                to_block = self.get_latest_block_number()

            logger.info(f"Получение событий с блока {from_block} по {to_block}")
            event_filter = self.contract.events.DocumentStored.create_filter(
                from_block=from_block,
                to_block=to_block
            )
            events = event_filter.get_all_entries()
            logger.info(f"Получено {len(events)} событий")
            return events
        except Exception as e:
            logger.error(f"Ошибка получения событий: {e}")
            return []

blockchain_service = BlockchainService()