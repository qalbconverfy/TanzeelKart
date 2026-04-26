from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Map root")
async def map_root():
    return {
        "success": True,
        "module": "map",
        "message": "Map API is available"
    }
