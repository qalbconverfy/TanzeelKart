from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Orders root")
async def orders_root():
    return {
        "success": True,
        "module": "orders",
        "message": "Orders API is available"
    }
