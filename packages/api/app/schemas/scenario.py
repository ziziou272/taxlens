"""Scenario schemas."""
from typing import Optional
from pydantic import BaseModel, Field


class ScenarioInput(BaseModel):
    name: str = "Scenario"
    scenario_type: str = "custom"
    filing_status: str = "single"
    wages: float = 0
    rsu_income: float = 0
    nso_income: float = 0
    bonus_income: float = 0
    short_term_gains: float = 0
    long_term_gains: float = 0
    qualified_dividends: float = 0
    interest_income: float = 0
    iso_bargain_element: float = 0
    state: str = "CA"
    itemized_deductions: float = 0


class ScenarioRunInput(BaseModel):
    baseline: ScenarioInput
    alternative: ScenarioInput


class ScenarioResultResponse(BaseModel):
    name: str
    total_tax: float
    effective_rate: float
    breakdown: dict = Field(default_factory=dict)


class ScenarioComparisonResponse(BaseModel):
    baseline: ScenarioResultResponse
    alternative: ScenarioResultResponse
    tax_savings: float
    savings_percentage: float
    breakdown_diff: dict = Field(default_factory=dict)


class ScenarioTypeResponse(BaseModel):
    type_id: str
    name: str
    description: str


class ScenarioSaveInput(BaseModel):
    name: str
    scenario_type: str = "custom"
    parameters: dict
    result: Optional[dict] = None
    total_tax: Optional[float] = None
    profile_id: Optional[str] = None


class ScenarioSaveResponse(BaseModel):
    id: str
    name: str
    message: str = "Scenario saved"
