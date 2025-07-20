from litestar.datastructures import UploadFile
from litestar.exceptions import ValidationException, HTTPException
from litestar.params import Body
from typing import Dict, Optional, Any

from .db import db
from .services.document_processor import document_processor
from .schemas import DocumentResponse, VerifyResponse, HealthResponse
from .logger import logger

class APIController:
    def __init__(self):
        self.db = db
        self.processor = document_processor
    
    async def health_check(self) -> HealthResponse:
        logger.info("Health check requested")
        return HealthResponse(
            status="ok",
            message="Document Hash API is running"
        )
    
    async def process_document(self, file: UploadFile) -> DocumentResponse:
        try:
            if not file:
                logger.warning("Файл не предоставлен")
                raise ValidationException("Файл не предоставлен")

            file_content = await file.read()
            filename = file.filename or "document.pdf"
            logger.info(f"Обработка документа: {filename}")

            # Process document
            verification_id, document_hash, _ = self.processor.process_document(file_content, filename)

            # Check if document already exists
            existing_hash = await self.db.get_by_document_hash(document_hash)
            if existing_hash:
                is_unique = False
                message = f"Документ уже существует с ID: {existing_hash['verification_id']}"
                logger.info(f"Документ уже существует: {document_hash}")
            else:
                # Check for ID collision
                existing_id = await self.db.get_by_verification_id(verification_id)
                if existing_id:
                    logger.info(f"Коллизия ID: {verification_id}, генерация нового ID")
                    while existing_id:
                        verification_id, _, _ = self.processor.process_document(file_content, filename)
                        existing_id = await self.db.get_by_verification_id(verification_id)

                is_unique = True
                message = "Документ готов к регистрации в блокчейне"
                logger.info(f"Документ уникален: {document_hash}")

            return DocumentResponse(
                verification_id=verification_id,
                document_hash=document_hash,
                is_unique=is_unique,
                message=message
            )

        except ValidationException as e:
            logger.warning(f"Ошибка валидации: {str(e)}")
            raise
        except ValueError as e:
            logger.warning(f"Ошибка значения: {str(e)}")
            raise ValidationException(str(e))
        except Exception as e:
            logger.error(f"Внутренняя ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def verify_document(
        self,
        file: Optional[UploadFile] = None,
        data: Optional[Dict[str, Any]] = Body(default=None)
    ) -> VerifyResponse:
        try:
            if file:
                logger.info(f"Верификация по файлу: {file.filename}")
                file_content = await file.read()
                result = await self.processor.verify_document(
                    self.db, 
                    file_content=file_content, 
                    filename=file.filename or "document.pdf"
                )
            elif data:
                verification_id = data.get("verification_id")
                document_hash = data.get("document_hash")
                
                if verification_id:
                    logger.info(f"Верификация по ID: {verification_id}")
                    result = await self.processor.verify_document(self.db, verification_id=verification_id)
                elif document_hash:
                    logger.info(f"Верификация по хешу: {document_hash}")
                    result = await self.processor.verify_document(self.db, document_hash=document_hash)
                else:
                    logger.warning("Не указан verification_id или document_hash")
                    raise ValidationException("Необходимо указать verification_id или document_hash")
            else:
                logger.warning("Не предоставлен файл или данные для верификации")
                raise ValidationException("Необходимо предоставить файл или данные для верификации")

            return VerifyResponse(**result)

        except ValidationException as e:
            logger.warning(f"Ошибка валидации: {str(e)}")
            raise
        except ValueError as e:
            logger.warning(f"Ошибка значения: {str(e)}")
            raise ValidationException(str(e))
        except Exception as e:
            logger.error(f"Внутренняя ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Singleton instance
api_controller = APIController()