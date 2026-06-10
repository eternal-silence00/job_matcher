from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, TIMESTAMP
from app.core.base import Base
from pgvector.sqlalchemy import Vector
from datetime import datetime, timezone

class Resume(Base):
    
    __tablename__ = "resumes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    filename: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(384), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc))