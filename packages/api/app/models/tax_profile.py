"""Tax profile model."""
import uuid
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class TaxProfile(Base):
    __tablename__ = "tax_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    filing_status: Mapped[str] = mapped_column(String, default="single")
    tax_year: Mapped[int] = mapped_column(default=2025)
    wages: Mapped[float] = mapped_column(Float, default=0)
    rsu_income: Mapped[float] = mapped_column(Float, default=0)
    state: Mapped[str] = mapped_column(String, default="CA")
    total_tax: Mapped[float] = mapped_column(Float, nullable=True)
    effective_rate: Mapped[float] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship(back_populates="profiles")  # type: ignore
    alerts: Mapped[list["Alert"]] = relationship(back_populates="profile", lazy="selectin")  # type: ignore
