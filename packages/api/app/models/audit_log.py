"""Audit log model."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True)
    action: Mapped[str] = mapped_column(String)  # login, logout, data_export, document_upload, plaid_link, account_deletion
    resource_type: Mapped[str] = mapped_column(String, nullable=True)  # document, plaid_item, user, etc.
    resource_id: Mapped[str] = mapped_column(String, nullable=True)
    details: Mapped[str] = mapped_column(Text, nullable=True)  # JSON extra info
    ip_address: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
