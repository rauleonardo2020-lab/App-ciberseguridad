from pydantic import BaseModel, EmailStr, Field, IPvAnyAddress
from typing import Any, Dict, List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ScanRequest(BaseModel):
    ip: IPvAnyAddress

class ScanResultOut(BaseModel):
    id: int
    ip: str
    scan_payload: Dict[str, Any]
    class Config:
        from_attributes = True
