"""Equity grant model."""
import uuid
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class EquityGrant(Base):
    __tablename__ = "equity_grants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profile_id: Mapped[str] = mapped_column(ForeignKey("tax_profiles.id"))
    grant_type: Mapped[str] = mapped_column(String)  # rsu, iso, nso, espp
    shares: Mapped[int] = mapped_column(Integer, default=0)
    grant_price: Mapped[float] = mapped_column(Float, default=0)
    current_value: Mapped[float] = mapped_column(Float, default=0)
