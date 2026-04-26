from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Notifications root")
async def notifications_root():
    return {
        "success": True,
        "module": "notifications",
        "message": "Notifications API is available"
    }
