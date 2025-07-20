import asyncio
import os
from typing import Optional
from .blockchain_service import blockchain_service
from ..models import database
from ..config import config


class BlockchainWorker:

    def __init__(self):
        self.running = False
        self.last_block_file = config.LAST_BLOCK_FILE
        self.scan_interval = 10

    def get_last_processed_block(self) -> int:
        try:
            if os.path.exists(self.last_block_file):
                with open(self.last_block_file, 'r') as f:
                    return int(f.read().strip())
            return blockchain_service.get_latest_block_number() - 100
        except Exception as e:
            print(f"❌ Ошибка чтения последнего блока: {e}")
            return blockchain_service.get_latest_block_number() - 100

    def save_last_processed_block(self, block_number: int):
        try:
            os.makedirs(os.path.dirname(self.last_block_file), exist_ok=True)
            with open(self.last_block_file, 'w') as f:
                f.write(str(block_number))
        except Exception as e:
            print(f"❌ Ошибка сохранения последнего блока: {e}")

    async def process_new_events(self):
        last_block = self.get_last_processed_block()
        current_block = blockchain_service.get_latest_block_number()

        if current_block <= last_block:
            return

        print(f"🔍 Сканирование блоков {last_block + 1} - {current_block}")

        try:
            events = blockchain_service.get_document_stored_events(
                from_block=last_block + 1,
                to_block=current_block
            )

            for event in events:
                await self.process_document_event(event)

            self.save_last_processed_block(current_block)

            if events:
                print(f"✅ Обработано {len(events)} событий")

        except Exception as e:
            print(f"❌ Ошибка обработки событий: {e}")

    async def process_document_event(self, event):
        try:
            creator = event.args.creator
            block_number = event.blockNumber
            tx_hash = event.transactionHash.hex()

            print(f"🔍 Processing event from block {block_number}, tx: {tx_hash}")
            print(f"🔍 Creator: {creator}")

            try:
                doc_count = await blockchain_service.get_creator_document_count(creator)
                print(f"🔍 Creator has {doc_count} documents")

                docs = await blockchain_service.get_documents_by_creator(creator)
                if docs:
                    last_verification_id = docs[-1]
                    print(f"🔍 Last verification_id: {last_verification_id}")

                    doc_info = await blockchain_service.get_document_info_by_id(last_verification_id)
                    if doc_info:
                        document_hash, creator_from_contract, timestamp = doc_info
                        print(f"🔍 Document hash: {document_hash}")

                        await database.insert_document(
                            verification_id=last_verification_id,
                            document_hash=document_hash,
                            creator_address=creator,
                            block_number=block_number
                        )

                        print(f"💾 Сохранен документ: {last_verification_id}")
                    else:
                        print("❌ Не удалось получить информацию о документе")
                else:
                    print("❌ Нет документов для создателя")

            except Exception as e:
                print(f"❌ Ошибка получения документов создателя: {e}")

        except Exception as e:
            print(f"❌ Ошибка обработки события: {e}")

    async def start(self):
        if not blockchain_service.is_connected():
            print("❌ Блокчейн не подключен, воркер не запущен")
            return

        self.running = True
        print("🚀 Blockchain worker запущен")

        while self.running:
            try:
                await self.process_new_events()
                await asyncio.sleep(self.scan_interval)
            except Exception as e:
                print(f"❌ Ошибка в воркере: {e}")
                await asyncio.sleep(self.scan_interval)

    def stop(self):
        self.running = False
        print("⏹️ Blockchain worker остановлен")


blockchain_worker = BlockchainWorker()