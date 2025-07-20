import hashlib
import time
from typing import Tuple, Dict, Any, Optional
from ..logger import logger

class DocumentProcessor:
    def __init__(self):
        self.chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    def generate_document_hash(self, file_content: bytes) -> str:
        return hashlib.sha512(file_content).hexdigest()
    
    def generate_verification_id(self, timestamp: Optional[int] = None) -> str:
        if timestamp is None:
            timestamp = int(time.time())
        
        result = ''
        seed = timestamp
        
        for _ in range(8):
            seed = (seed * 1103515245 + 12345) & 0x7fffffff
            result += self.chars[seed % len(self.chars)]
        
        return result
    
    def validate_pdf(self, file_content: bytes) -> bool:
        return len(file_content) >= 4 and file_content[:4] == b'%PDF'
    
    def process_document(self, file_content: bytes, filename: str) -> Tuple[str, str, bool]:
        if not self.validate_pdf(file_content):
            logger.error(f"Файл {filename} не является PDF документом")
            raise ValueError("Файл не является PDF документом")
        
        document_hash = self.generate_document_hash(file_content)
        verification_id = self.generate_verification_id()
        
        logger.info(f"Документ {filename} обработан, verification_id: {verification_id}")
        return verification_id, document_hash, True
    
    async def verify_document(self, db, file_content: Optional[bytes] = None, 
                             filename: Optional[str] = None,
                             verification_id: Optional[str] = None, 
                             document_hash: Optional[str] = None) -> Dict[str, Any]:
        record = None
        
        if file_content:
            _, hash_value, _ = self.process_document(file_content, filename or "document.pdf")
            record = await db.get_by_document_hash(hash_value)
        elif verification_id:
            record = await db.get_by_verification_id(verification_id)
        elif document_hash:
            record = await db.get_by_document_hash(document_hash)
        
        if record:
            return {
                "verified": True,
                "message": "Документ найден в блокчейне",
                "timestamp": record['timestamp'].isoformat() if record['timestamp'] else None,
                "creator": record['creator_address']
            }
        else:
            return {
                "verified": False,
                "message": "Документ не найден в блокчейне"
            }

# Singleton instance
document_processor = DocumentProcessor()