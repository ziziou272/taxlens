"""Alert model."""
import uuid
from sqlalchemy import String, Float, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String, index=True, default="anonymous")
    profile_id: Mapped[str] = mapped_column(ForeignKey("tax_profiles.id"))
    severity: Mapped[str] = mapped_column(String)  # info, warning, critical
    category: Mapped[str] = mapped_column(String)
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float, nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)

    profile: Mapped["TaxProfile"] = relationship(back_populates="alerts")  # type: ignore
