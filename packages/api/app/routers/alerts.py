"""Alert endpoints."""
from fastapi import APIRouter, Depends

from app.dependencies import require_auth
from app.schemas.alert import AlertCheckInput, AlertCheckResponse, ProfileAlertResponse
from app.services import alert_service

router = APIRouter()


@router.post("/check", response_model=AlertCheckResponse)
async def check_alerts(inp: AlertCheckInput):
    """Run red flag checks on provided tax data. Public endpoint."""
    return alert_service.check_alerts(inp)


@router.get("/{profile_id}", response_model=ProfileAlertResponse)
async def get_profile_alerts(profile_id: str, user_id: str = Depends(require_auth)):
    """Get alerts for a profile. Protected."""
    return ProfileAlertResponse(profile_id=profile_id, alerts=[])


@router.post("/{alert_id}/dismiss")
async def dismiss_alert(alert_id: str, user_id: str = Depends(require_auth)):
    """Dismiss an alert. Protected."""
    return {"alert_id": alert_id, "dismissed": True}
