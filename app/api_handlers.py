from litestar.datastructures import UploadFile
from litestar.exceptions import ValidationException, HTTPException
from litestar.params import Body
from litestar.response import Response
import msgspec
from typing import Dict, Optional, Union, Any

from app.models import database
from app.schemas import (
    DocumentProcessResponse, DocumentVerifyResponse, HealthResponse, ErrorResponse
)
from app.services.document_processor import DocumentProcessor


class APIController:
    @staticmethod
    async def health_check() -> HealthResponse:
        return HealthResponse(
            status="ok",
            message="Document Hash API is running"
        )

    @staticmethod
    async def process_document(file: UploadFile) -> DocumentProcessResponse:
        try:
            if not file:
                raise ValidationException("Файл не предоставлен")

            file_content = await file.read()
            filename = file.filename or "document.pdf"

            verification_id, document_hash, is_unique = DocumentProcessor.process_document(
                file_content, filename
            )

            existing_hash = await database.get_by_document_hash(document_hash)
            if existing_hash:
                is_unique = False
                message = f"Документ уже существует с ID: {existing_hash['verification_id']}"
            else:
                existing_id = await database.get_by_verification_id(verification_id)
                if existing_id:
                    while existing_id:
                        verification_id, _, _ = DocumentProcessor.process_document(file_content, filename)
                        existing_id = await database.get_by_verification_id(verification_id)

                is_unique = True
                message = "Документ готов к регистрации в блокчейне"

            return DocumentProcessResponse(
                verification_id=verification_id,
                document_hash=document_hash,
                is_unique=is_unique,
                message=message
            )

        except ValidationException as e:
            raise e
        except ValueError as e:
            raise ValidationException(str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def verify_document(
        file: Optional[UploadFile] = None,
        data: Optional[Dict[str, Any]] = Body(default=None)
    ) -> DocumentVerifyResponse:
        try:
            if file:
                file_content = await file.read()
                _, document_hash, _ = DocumentProcessor.process_document(file_content, file.filename or "document.pdf")
                record = await database.get_by_document_hash(document_hash)
            elif data:
                verification_id = data.get("verification_id")
                document_hash = data.get("document_hash")

                if verification_id:
                    record = await database.get_by_verification_id(verification_id)
                elif document_hash:
                    record = await database.get_by_document_hash(document_hash)
                else:
                    raise ValidationException("Необходимо указать verification_id или document_hash")
            else:
                raise ValidationException("Необходимо предоставить файл или данные для верификации")

            if record:
                return DocumentVerifyResponse(
                    verified=True,
                    message="Документ найден в блокчейне",
                    timestamp=record['timestamp'].isoformat() if record['timestamp'] else None,
                    creator=record['creator_address']
                )
            else:
                return DocumentVerifyResponse(
                    verified=False,
                    message="Документ не найден в блокчейне"
                )

        except ValidationException as e:
            raise e
        except ValueError as e:
            raise ValidationException(str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
