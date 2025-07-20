from web3 import Web3
import asyncio
import os
from typing import Optional, Tuple, List, Any, Dict
from .config import config
from .logger import logger
from .db import db

class Blockchain:
    def __init__(self):
        # Core blockchain properties
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        self.contract = self.w3.eth.contract(
            address=config.CONTRACT_ADDRESS,
            abi=config.CONTRACT_ABI
        )
        
        # Worker properties
        self.running = False
        self.last_block_file = config.LAST_BLOCK_FILE
        self.scan_interval = 10
        
        logger.info(f"Blockchain initialized with RPC: {config.RPC_URL}")
    
    def is_connected(self) -> bool:
        try:
            connected = self.w3.is_connected()
            if connected:
                logger.info("Blockchain connection established")
            else:
                logger.warning("Blockchain connection failed")
            return connected
        except Exception as e:
            logger.error(f"Ошибка подключения к блокчейну: {e}")
            return False
    
    async def check_hash_exists(self, document_hash: str) -> bool:
        try:
            return self.contract.functions.hashExists(document_hash).call()
        except Exception as e:
            logger.error(f"Ошибка проверки хеша в блокчейне: {e}")
            return False
    
    async def get_document_info_by_id(self, verification_id: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfo(verification_id).call()
            return (result[0], result[1], result[2]) if result[0] else None
        except Exception as e:
            logger.error(f"Ошибка получения документа по ID: {e}")
            return None
    
    async def get_document_info_by_hash(self, document_hash: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfoByHash(document_hash).call()
            return (result[0], result[1], result[2]) if result[0] else None
        except Exception as e:
            logger.error(f"Ошибка получения документа по хешу: {e}")
            return None
    
    async def get_creator_document_count(self, creator_address: str) -> int:
        try:
            return self.contract.functions.getCreatorDocumentCount(creator_address).call()
        except Exception as e:
            logger.error(f"Ошибка получения количества документов: {e}")
            return 0
    
    async def get_documents_by_creator(self, creator_address: str) -> List[str]:
        try:
            return self.contract.functions.getDocumentsByCreator(creator_address).call()
        except Exception as e:
            logger.error(f"Ошибка получения документов создателя: {e}")
            return []
    
    def get_latest_block_number(self) -> int:
        try:
            return self.w3.eth.block_number
        except Exception as e:
            logger.error(f"Ошибка получения номера блока: {e}")
            return 0
    
    def get_document_stored_events(self, from_block: int, to_block: int = None) -> List[Any]:
        try:
            if to_block is None:
                to_block = self.get_latest_block_number()
            
            event_filter = self.contract.events.DocumentStored.create_filter(
                from_block=from_block,
                to_block=to_block
            )
            return event_filter.get_all_entries()
        except Exception as e:
            logger.error(f"Ошибка получения событий: {e}")
            return []
    
    # Worker methods
    def get_last_processed_block(self) -> int:
        try:
            if os.path.exists(self.last_block_file):
                with open(self.last_block_file, 'r') as f:
                    return int(f.read().strip())
            return self.get_latest_block_number() - 100
        except Exception as e:
            default_block = self.get_latest_block_number() - 100
            logger.error(f"Ошибка чтения последнего блока: {e}, используем: {default_block}")
            return default_block
    
    def save_last_processed_block(self, block_number: int) -> None:
        try:
            os.makedirs(os.path.dirname(self.last_block_file), exist_ok=True)
            with open(self.last_block_file, 'w') as f:
                f.write(str(block_number))
        except Exception as e:
            logger.error(f"Ошибка сохранения последнего блока: {e}")
    
    async def process_document_event(self, event: Any) -> None:
        try:
            creator = event.args.creator
            block_number = event.blockNumber
            
            docs = await self.get_documents_by_creator(creator)
            if not docs:
                return
                
            last_verification_id = docs[-1]
            doc_info = await self.get_document_info_by_id(last_verification_id)
            
            if doc_info:
                document_hash, _, _ = doc_info
                await db.insert_document(
                    verification_id=last_verification_id,
                    document_hash=document_hash,
                    creator_address=creator,
                    block_number=block_number
                )
        except Exception as e:
            logger.error(f"Ошибка обработки события: {e}")
    
    async def process_new_events(self) -> None:
        last_block = self.get_last_processed_block()
        current_block = self.get_latest_block_number()
        
        if current_block <= last_block:
            return
            
        try:
            events = self.get_document_stored_events(
                from_block=last_block + 1,
                to_block=current_block
            )
            
            for event in events:
                await self.process_document_event(event)
                
            self.save_last_processed_block(current_block)
        except Exception as e:
            logger.error(f"Ошибка обработки событий: {e}")
    
    async def start_worker(self) -> None:
        if not self.is_connected():
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
    
    def stop_worker(self) -> None:
        self.running = False
        logger.info("Blockchain worker остановлен")

# Singleton instance
blockchain = Blockchain()