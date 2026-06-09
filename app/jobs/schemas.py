from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class JobCreate(BaseModel):
    title: str = Field(... ,min_length=3, max_length=200)
    description: str = Field(..., min_length=3, max_length=1000)
    salary_from: Optional[float] = Field(None, ge=0)
    salary_to: Optional[float] = Field(None, ge=0)
    company: str = Field(..., min_length=1, max_length=50)
    url: str = Field(...)
    location: str = Field(..., min_length=2, max_length=50)
    published_at: datetime = Field(...)
    
    
class JobResponse(BaseModel):
    id: int
    title: str 
    description: str 
    salary_from: Optional[float] 
    salary_to: Optional[float] 
    company: str 
    url: str 
    location: str 
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)