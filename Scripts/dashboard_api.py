import os
from fastapi import APIRouter, Depends, HTTPException
from api import require_auth, traffic_analysis, load_analysis, ads_analysis, user_analysis, security_analysis

router = APIRouter()

@router.get("/dashboard-data")
def get_dashboard_data(_: str = Depends(require_auth)):
    try:
        return {
            "traffic": traffic_analysis(),
            "load": load_analysis(),
            "ads": ads_analysis(),
            "users": user_analysis(),
            "security": security_analysis()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
