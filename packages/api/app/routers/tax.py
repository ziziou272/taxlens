"""Tax calculation endpoints."""
from fastapi import APIRouter, HTTPException

from app.schemas.tax import TaxInput, TaxBreakdownResponse, WithholdingGapInput, WithholdingGapResponse
from app.services import tax_service

router = APIRouter()


@router.post("/calculate", response_model=TaxBreakdownResponse)
async def calculate_tax(inp: TaxInput):
    """Full tax calculation."""
    return tax_service.calculate(inp)


@router.get("/breakdown/{profile_id}", response_model=TaxBreakdownResponse)
async def get_breakdown(profile_id: str):
    """Get tax breakdown for a saved profile. Stub — returns 404 for now."""
    raise HTTPException(status_code=404, detail=f"Profile {profile_id} not found")


@router.post("/withholding-gap", response_model=WithholdingGapResponse)
async def withholding_gap(inp: WithholdingGapInput):
    """Compare YTD withholding vs projected liability."""
    return tax_service.withholding_gap(inp)
