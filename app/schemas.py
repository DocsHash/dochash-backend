import msgspec
from typing import Optional, TypeVar, Type, Any

# Response schemas
class DocumentResponse(msgspec.Struct):
    verification_id: str
    document_hash: str
    is_unique: bool
    message: str

class VerifyResponse(msgspec.Struct):
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

# Type variable for generic serialization
T = TypeVar('T')

class Serializer:
    @staticmethod
    def to_json(obj: Any) -> bytes:
        """Convert object to JSON bytes"""
        return msgspec.json.encode(obj)
    
    @staticmethod
    def from_json(data: bytes, type_: Type[T]) -> T:
        """Convert JSON bytes to object"""
        return msgspec.json.decode(data, type=type_)

# Singleton instance
serializer = Serializer()