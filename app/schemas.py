import msgspec
from typing import Optional, Union, Dict, Any

class DocumentProcessRequest(msgspec.Struct):
    file: bytes
    filename: str

class DocumentProcessResponse(msgspec.Struct):
    verification_id: str
    document_hash: str
    is_unique: bool
    message: str

class DocumentVerifyRequest(msgspec.Struct):
    verification_id: Optional[str] = None
    document_hash: Optional[str] = None
    file: Optional[bytes] = None
    filename: Optional[str] = None

class DocumentVerifyResponse(msgspec.Struct):
    verified: bool
    message: str
    timestamp: Optional[str] = None
    creator: Optional[str] = None

class HealthResponse(msgspec.Struct):
    status: str
    message: str

class ErrorResponse(msgspec.Struct):
    error: str
    detail: Optional[str] = None
