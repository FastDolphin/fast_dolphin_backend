from pydantic import BaseModel, Field
from typing import Dict, Optional
import uuid


class Messages(BaseModel):
    TgId: Optional[int] = None
    ApiKey: str
    Messages: Dict[str, str] = {}


class MessagesWithId(Messages):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
