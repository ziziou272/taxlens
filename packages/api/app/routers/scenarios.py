"""Scenario endpoints."""
import uuid
from fastapi import APIRouter, Depends

from app.dependencies import require_auth
from app.schemas.scenario import (
    ScenarioRunInput,
    ScenarioComparisonResponse,
    ScenarioTypeResponse,
    ScenarioSaveInput,
    ScenarioSaveResponse,
)
from app.services import scenario_service

router = APIRouter()


@router.get("/types", response_model=list[ScenarioTypeResponse])
async def get_scenario_types():
    """List available scenario types. Public."""
    return scenario_service.get_types()


@router.post("/run", response_model=ScenarioComparisonResponse)
async def run_scenario(inp: ScenarioRunInput):
    """Execute what-if scenario comparison. Public."""
    return scenario_service.run_comparison(inp)


@router.post("/save", response_model=ScenarioSaveResponse)
async def save_scenario(inp: ScenarioSaveInput, user_id: str = Depends(require_auth)):
    """Save a scenario result. Protected."""
    return ScenarioSaveResponse(id=str(uuid.uuid4()), name=inp.name)
