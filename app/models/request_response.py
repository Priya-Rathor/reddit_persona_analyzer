from pydantic import BaseModel
from typing import Optional, Dict

class UserRequest(BaseModel):
    username: str
    limit: Optional[int] = 75

class PersonaResponse(BaseModel):
    success: bool
    message: str
    persona: Optional[str] = None
    raw_data: Optional[Dict] = None
