"""AI Tax Advisor service using Claude API."""
from __future__ import annotations

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from app.config import settings

SYSTEM_PROMPT = (
    "You are a tax advisor for high-income tech professionals. "
    "Explain tax concepts clearly. Never give specific legal advice - "
    "recommend consulting a CPA for complex situations. "
    "Focus on RSU, ISO, ESPP, capital gains, AMT, and equity compensation topics."
)


def _require_anthropic():
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="AI advisor not configured")


def _get_client():
    import anthropic
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def explain(tax_context: dict, question: str) -> StreamingResponse:
    """Explain a tax situation in plain English with streaming."""
    _require_anthropic()
    client = _get_client()

    context_str = f"User's tax situation: {tax_context}" if tax_context else ""
    prompt = f"{context_str}\n\nPlease explain: {question}"

    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")


async def recommend(tax_context: dict) -> StreamingResponse:
    """Get personalized tax recommendations with streaming."""
    _require_anthropic()
    client = _get_client()

    prompt = (
        f"Based on this tax calculation result, identify optimization opportunities "
        f"(RSU timing, ISO exercise strategy, LTCG vs STCG, ESPP holding periods, "
        f"tax-loss harvesting, etc.):\n\n{tax_context}\n\n"
        f"Provide specific, actionable recommendations ranked by potential tax savings."
    )

    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")


async def ask(tax_context: dict | None, question: str) -> StreamingResponse:
    """Free-form tax Q&A with streaming."""
    _require_anthropic()
    client = _get_client()

    context_str = f"Context about my tax situation: {tax_context}\n\n" if tax_context else ""
    prompt = f"{context_str}{question}"

    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                yield text

    return StreamingResponse(generate(), media_type="text/plain")
