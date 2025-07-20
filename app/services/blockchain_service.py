from web3 import Web3
from typing import Optional, Tuple
from ..config import config


class BlockchainService:

    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider(config.RPC_URL))
        self.contract = self.w3.eth.contract(
            address=config.CONTRACT_ADDRESS,
            abi=config.CONTRACT_ABI
        )

    def is_connected(self) -> bool:
        try:
            return self.w3.is_connected()
        except:
            return False

    async def check_hash_exists(self, document_hash: str) -> bool:
        try:
            return self.contract.functions.hashExists(document_hash).call()
        except Exception as e:
            print(f"❌ Ошибка проверки хеша в блокчейне: {e}")
            return False

    async def get_document_info_by_id(self, verification_id: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfo(verification_id).call()
            if result[0]:
                return result[0], result[1], result[2]
            return None
        except Exception as e:
            print(f"❌ Ошибка получения документа по ID: {e}")
            return None

    async def get_document_info_by_hash(self, document_hash: str) -> Optional[Tuple[str, str, int]]:
        try:
            result = self.contract.functions.getDocumentInfoByHash(document_hash).call()
            if result[0]:
                return result[0], result[1], result[2]
            return None
        except Exception as e:
            print(f"❌ Ошибка получения документа по хешу: {e}")
            return None

    async def get_creator_document_count(self, creator_address: str) -> int:
        try:
            return self.contract.functions.getCreatorDocumentCount(creator_address).call()
        except Exception as e:
            print(f"❌ Ошибка получения количества документов: {e}")
            return 0

    async def get_documents_by_creator(self, creator_address: str) -> list:
        try:
            return self.contract.functions.getDocumentsByCreator(creator_address).call()
        except Exception as e:
            print(f"❌ Ошибка получения документов создателя: {e}")
            return []

    def get_latest_block_number(self) -> int:
        try:
            return self.w3.eth.block_number
        except Exception as e:
            print(f"❌ Ошибка получения номера блока: {e}")
            return 0

    def get_document_stored_events(self, from_block: int, to_block: int = None):
        try:
            if to_block is None:
                to_block = self.get_latest_block_number()

            event_filter = self.contract.events.DocumentStored.create_filter(
                from_block=from_block,
                to_block=to_block
            )
            return event_filter.get_all_entries()
        except Exception as e:
            print(f"❌ Ошибка получения событий: {e}")
            return []


blockchain_service = BlockchainService()