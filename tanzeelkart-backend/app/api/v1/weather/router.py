from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_weather():
    return {"message": "Weather API - Coming Soon"}