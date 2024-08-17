from fastapi import APIRouter, HTTPException
from ..services import school_service

router = APIRouter()

@router.get("/schools")
async def get_schools():
    try:
        schools = school_service.get_all_schools()
        return {
            "type": "FeatureCollection",
            "features": schools
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
