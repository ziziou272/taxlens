"""Alert schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class AlertCheckInput(BaseModel):
    total_income: float
    total_tax_liability: float
    total_withheld: float
    long_term_gains: float = 0
    short_term_gains: float = 0
    rsu_income: float = 0
    iso_bargain_element: float = 0
    filing_status: str = "single"
    state: str = "CA"
    prior_year_tax: Optional[float] = None


class AlertResponse(BaseModel):
    severity: str
    category: str
    title: str
    message: str
    amount: Optional[float] = None
    action_required: Optional[str] = None
    deadline: Optional[str] = None


class AlertCheckResponse(BaseModel):
    summary: str
    alerts: list[AlertResponse] = Field(default_factory=list)
    has_critical: bool = False


class ProfileAlertResponse(BaseModel):
    profile_id: str
    alerts: list[AlertResponse] = Field(default_factory=list)
