from litestar.datastructures import UploadFile
from litestar.exceptions import ValidationException, HTTPException
from litestar.params import Body
from typing import Dict, Optional, Any

from app.models import database
from app.schemas import (
    DocumentProcessResponse, DocumentVerifyResponse, HealthResponse
)
from app.services.document_processor import document_processor
from app.logger import logger

class APIController:
    def __init__(self):
        self.db = database
        self.processor = document_processor

    async def health_check(self) -> HealthResponse:
        logger.info("Health check requested")
        return HealthResponse(
            status="ok",
            message="Document Hash API is running"
        )

    async def process_document(self, file: UploadFile) -> DocumentProcessResponse:
        try:
            if not file:
                logger.warning("Файл не предоставлен")
                raise ValidationException("Файл не предоставлен")

            file_content = await file.read()
            filename = file.filename or "document.pdf"
            logger.info(f"Обработка документа: {filename}")

            verification_id, document_hash, is_unique = self.processor.process_document(
                file_content, filename
            )

            existing_hash = await self.db.get_by_document_hash(document_hash)
            if existing_hash:
                is_unique = False
                message = f"Документ уже существует с ID: {existing_hash['verification_id']}"
                logger.info(f"Документ уже существует: {document_hash}")
            else:
                existing_id = await self.db.get_by_verification_id(verification_id)
                if existing_id:
                    logger.info(f"Коллизия ID: {verification_id}, генерация нового ID")
                    while existing_id:
                        verification_id, _, _ = self.processor.process_document(file_content, filename)
                        existing_id = await self.db.get_by_verification_id(verification_id)

                is_unique = True
                message = "Документ готов к регистрации в блокчейне"
                logger.info(f"Документ уникален: {document_hash}")

            return DocumentProcessResponse(
                verification_id=verification_id,
                document_hash=document_hash,
                is_unique=is_unique,
                message=message
            )

        except ValidationException as e:
            logger.warning(f"Ошибка валидации: {str(e)}")
            raise e
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
    ) -> DocumentVerifyResponse:
        try:
            if file:
                logger.info(f"Верификация по файлу: {file.filename}")
                file_content = await file.read()
                _, document_hash, _ = self.processor.process_document(file_content, file.filename or "document.pdf")
                record = await self.db.get_by_document_hash(document_hash)
            elif data:
                verification_id = data.get("verification_id")
                document_hash = data.get("document_hash")
                
                if verification_id:
                    logger.info(f"Верификация по ID: {verification_id}")
                    record = await self.db.get_by_verification_id(verification_id)
                elif document_hash:
                    logger.info(f"Верификация по хешу: {document_hash}")
                    record = await self.db.get_by_document_hash(document_hash)
                else:
                    logger.warning("Не указан verification_id или document_hash")
                    raise ValidationException("Необходимо указать verification_id или document_hash")
            else:
                logger.warning("Не предоставлен файл или данные для верификации")
                raise ValidationException("Необходимо предоставить файл или данные для верификации")

            if record:
                logger.info(f"Документ найден: {record['verification_id']}")
                return DocumentVerifyResponse(
                    verified=True,
                    message="Документ найден в блокчейне",
                    timestamp=record['timestamp'].isoformat() if record['timestamp'] else None,
                    creator=record['creator_address']
                )
            else:
                logger.info("Документ не найден")
                return DocumentVerifyResponse(
                    verified=False,
                    message="Документ не найден в блокчейне"
                )

        except ValidationException as e:
            logger.warning(f"Ошибка валидации: {str(e)}")
            raise e
        except ValueError as e:
            logger.warning(f"Ошибка значения: {str(e)}")
            raise ValidationException(str(e))
        except Exception as e:
            logger.error(f"Внутренняя ошибка: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

api_controller = APIController()
