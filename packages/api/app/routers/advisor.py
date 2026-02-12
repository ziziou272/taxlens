"""AI Tax Advisor endpoints."""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.dependencies import require_auth
from app.services import advisor_service

router = APIRouter()


class ExplainRequest(BaseModel):
    tax_context: dict = {}
    question: str


class RecommendRequest(BaseModel):
    tax_context: dict


class AskRequest(BaseModel):
    tax_context: dict | None = None
    question: str


@router.post("/explain")
async def explain(body: ExplainRequest, user_id: str = Depends(require_auth)):
    return await advisor_service.explain(body.tax_context, body.question)


@router.post("/recommend")
async def recommend(body: RecommendRequest, user_id: str = Depends(require_auth)):
    return await advisor_service.recommend(body.tax_context)


@router.post("/ask")
async def ask(body: AskRequest, user_id: str = Depends(require_auth)):
    return await advisor_service.ask(body.tax_context, body.question)
