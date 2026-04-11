from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_map():
    return {"message": "Map API - Coming Soon"}
    