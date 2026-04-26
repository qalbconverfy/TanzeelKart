from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Users root")
async def users_root():
    return {
        "success": True,
        "module": "users",
        "message": "Users API is available"
    }
