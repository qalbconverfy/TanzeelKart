from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Auth root")
async def auth_root():
    return {
        "success": True,
        "module": "auth",
        "message": "Auth API is available"
    }
