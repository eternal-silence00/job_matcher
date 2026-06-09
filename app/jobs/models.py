from sqlalchemy.orm import mapped_column, Mapped
from app.core.base import Base
from typing import Optional
from datetime import datetime, timezone
from pgvector.sqlalchemy import Vector
from sqlalchemy import TIMESTAMP

class Job(Base):
    
    __tablename__ = "jobs"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    salary_from: Mapped[Optional[float]]
    salary_to: Mapped[Optional[float]]
    company: Mapped[str] = mapped_column(nullable=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    location: Mapped[str] = mapped_column(nullable=False)
    published_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    embedding: Mapped[list] = mapped_column(Vector(384), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda:datetime.now(timezone.utc))
    