"""Document model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True, default="anonymous")
    profile_id: Mapped[str] = mapped_column(String, nullable=True)
    filename: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String, default="")
    doc_type: Mapped[str] = mapped_column(String, default="unknown")  # w2, 1099-b, 1099-div, 3922
    status: Mapped[str] = mapped_column(String, default="pending")  # pending, extracted, confirmed, error
    extracted_data: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON string
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
