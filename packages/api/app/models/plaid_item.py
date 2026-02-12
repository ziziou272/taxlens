"""Plaid item model for storing connected accounts."""
import uuid
from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from datetime import datetime


class PlaidItem(Base):
    __tablename__ = "plaid_items"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True)
    access_token_encrypted: Mapped[str] = mapped_column(String)
    item_id: Mapped[str] = mapped_column(String, unique=True)
    institution_id: Mapped[str] = mapped_column(String, default="")
    institution_name: Mapped[str] = mapped_column(String, default="")
    status: Mapped[str] = mapped_column(String, default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
