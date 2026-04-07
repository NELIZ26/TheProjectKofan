from fastapi import APIRouter, Depends
from backend.dependencies.auth import required_admin
from backend.services.dashboard_service import get_dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("", dependencies=[Depends(required_admin)])
async def get_dashboard_data():
    return await get_dashboard_metrics()