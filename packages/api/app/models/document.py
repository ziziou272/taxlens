"""Document model."""
import uuid
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("tax_profiles.id"))
    filename: Mapped[str] = mapped_column(String)
    doc_type: Mapped[str] = mapped_column(String)  # w2, 1099, etc.
    status: Mapped[str] = mapped_column(String, default="pending")
