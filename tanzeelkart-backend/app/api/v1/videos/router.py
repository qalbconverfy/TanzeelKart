from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Videos root")
async def videos_root():
    return {
        "success": True,
        "module": "videos",
        "message": "Videos API is available"
    }
