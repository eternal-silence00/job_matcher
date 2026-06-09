from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserCreate(BaseModel):
    email: str
    password: str
    
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