"""Scenario endpoints."""
import uuid
from fastapi import APIRouter

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
    """List available scenario types."""
    return scenario_service.get_types()


@router.post("/run", response_model=ScenarioComparisonResponse)
async def run_scenario(inp: ScenarioRunInput):
    """Execute what-if scenario comparison."""
    return scenario_service.run_comparison(inp)


@router.post("/save", response_model=ScenarioSaveResponse)
async def save_scenario(inp: ScenarioSaveInput):
    """Save a scenario result. In-memory stub for now."""
    return ScenarioSaveResponse(id=str(uuid.uuid4()), name=inp.name)
