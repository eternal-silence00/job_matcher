from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import TIMESTAMP, ForeignKey, String
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
    
    
class RefreshToken(Base):
    
    __tablename__ = "refresh_tokens"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))
    revoked_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP(timezone=True), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(nullable=True)
    ip: Mapped[Optional[str]] = mapped_column(String(45),nullable=True)
    replaced_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("refresh_tokens.id", ondelete="SET NULL"), nullable=True)
    