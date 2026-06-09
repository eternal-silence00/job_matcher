from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import TIMESTAMP
from app.core.base import Base
from datetime import datetime, timezone
from typing import Optional

class User(Base):
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    hashed_password: Mapped[Optional[str]]
    role: Mapped[str] = mapped_column(nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))