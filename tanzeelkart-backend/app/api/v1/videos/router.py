from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_videos():
    return {"message": "Videos API - Coming Soon"}
    