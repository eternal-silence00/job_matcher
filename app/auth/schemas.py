from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    
class UserOauthCreate(BaseModel):
    email: str
    password: Optional[str] = None
    
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)
    
class RefreshRequest(BaseModel):
    refresh_token: str