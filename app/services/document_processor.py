import hashlib
import time
from typing import Tuple
from app.logger import logger

class DocumentProcessor:
    def __init__(self):
        self.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'

    def generate_document_hash(self, file_content: bytes) -> str:
        return hashlib.sha512(file_content).hexdigest()

    def generate_verification_id(self, timestamp: int = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())

        result = ''
        seed = timestamp

        for i in range(8):
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            result += self.chars[seed % len(self.chars)]

        return result

    def validate_pdf(self, file_content: bytes) -> bool:
        if len(file_content) < 4:
            return False
        return file_content[:4] == b'%PDF'

    def process_document(self, file_content: bytes, filename: str) -> Tuple[str, str, bool]:
        if not self.validate_pdf(file_content):
            logger.error(f"Файл {filename} не является PDF документом")
            raise ValueError("Файл не является PDF документом")

        document_hash = self.generate_document_hash(file_content)
        verification_id = self.generate_verification_id()
        
        logger.info(f"Документ {filename} обработан, verification_id: {verification_id}")
        return verification_id, document_hash, True

document_processor = DocumentProcessor()