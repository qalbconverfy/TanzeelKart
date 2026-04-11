from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Weather root")
async def weather_root():
    return {
        "success": True,
        "module": "weather",
        "message": "Weather API is available"
    }
