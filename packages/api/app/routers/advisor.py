"""AI Tax Advisor endpoints."""
from fastapi import APIRouter
from pydantic import BaseModel

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
async def explain(body: ExplainRequest):
    return await advisor_service.explain(body.tax_context, body.question)


@router.post("/recommend")
async def recommend(body: RecommendRequest):
    return await advisor_service.recommend(body.tax_context)


@router.post("/ask")
async def ask(body: AskRequest):
    return await advisor_service.ask(body.tax_context, body.question)
