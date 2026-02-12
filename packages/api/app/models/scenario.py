"""Scenario model."""
import uuid
from sqlalchemy import String, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True, default="anonymous")
    profile_id: Mapped[str] = mapped_column(ForeignKey("tax_profiles.id"), nullable=True)
    name: Mapped[str] = mapped_column(String)
    scenario_type: Mapped[str] = mapped_column(String)
    parameters: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict] = mapped_column(JSON, nullable=True)
    total_tax: Mapped[float] = mapped_column(Float, nullable=True)
