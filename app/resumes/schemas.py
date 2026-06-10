from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ResumeResponse(BaseModel):
    
    id: int
    filename: str
    file_url: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)