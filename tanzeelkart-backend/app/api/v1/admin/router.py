from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Admin root")
async def admin_root():
    return {
        "success": True,
        "module": "admin",
        "message": "Admin API is available"
    }
