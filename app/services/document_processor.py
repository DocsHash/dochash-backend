import hashlib
import random
import time
from typing import Tuple


class DocumentProcessor:

    @staticmethod
    def generate_document_hash(file_content: bytes) -> str:
        return hashlib.sha512(file_content).hexdigest()

    @staticmethod
    def generate_verification_id_() -> str:
        timestamp = str(int(time.time()))[-8:]
        random_part = str(random.randint(100, 999))
        return f"{timestamp}{random_part}"

    @staticmethod
    def generate_verification_id(timestamp: int = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())

        chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        result = ''
        seed = timestamp

        for i in range(8):
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            result += chars[seed % len(chars)]

        return result

    @staticmethod
    def validate_pdf(file_content: bytes) -> bool:
        if len(file_content) < 4:
            return False
        return file_content[:4] == b'%PDF'

    @staticmethod
    def process_document(file_content: bytes, filename: str) -> Tuple[str, str, bool]:
        if not DocumentProcessor.validate_pdf(file_content):
            raise ValueError("Файл не является PDF документом")

        document_hash = DocumentProcessor.generate_document_hash(file_content)
        verification_id = DocumentProcessor.generate_verification_id()

        return verification_id, document_hash, True