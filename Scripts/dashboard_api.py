import os
from fastapi import APIRouter, Depends, HTTPException
from api import require_auth, traffic_analysis, load_analysis, ads_analysis, user_analysis, security_analysis

router = APIRouter()

@router.get("/dashboard-data/traffic")
def get_traffic(_: str = Depends(require_auth)):
    try:
        return traffic_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data/load")
def get_load(_: str = Depends(require_auth)):
    try:
        return load_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data/ads")
def get_ads(_: str = Depends(require_auth)):
    try:
        return ads_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data/users")
def get_users(_: str = Depends(require_auth)):
    try:
        return user_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data/security")
def get_security(_: str = Depends(require_auth)):
    try:
        return security_analysis()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))