"""Alert endpoints."""
from fastapi import APIRouter, HTTPException

from app.schemas.alert import AlertCheckInput, AlertCheckResponse, ProfileAlertResponse
from app.services import alert_service

router = APIRouter()


@router.post("/check", response_model=AlertCheckResponse)
async def check_alerts(inp: AlertCheckInput):
    """Run red flag checks on provided tax data."""
    return alert_service.check_alerts(inp)


@router.get("/{profile_id}", response_model=ProfileAlertResponse)
async def get_profile_alerts(profile_id: str):
    """Get alerts for a profile. Stub."""
    return ProfileAlertResponse(profile_id=profile_id, alerts=[])


@router.post("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str):
    """Dismiss an alert. Stub."""
    return {"alert_id": alert_id, "dismissed": True}
