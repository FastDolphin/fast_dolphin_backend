from typing import Optional, Dict, Any

from pydantic import BaseModel, Field
import uuid


class APIKeyMetadata(BaseModel):
    Name: str
    Surname: str
    Days: int


class APIKeyRequest(BaseModel):
    ApiKey: str
    Metadata: APIKeyMetadata


class APIKey(APIKeyRequest):
    GeneratedAt: str
    ExpiresAt: str


class APIKeyWithId(APIKey):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")


class APIKeyResponse(BaseModel):
    Allowed: bool = Field(default_factory=lambda: False)
    ExpiresAt: str = Field(default_factory=lambda: "")
