from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Delivery root")
async def delivery_root():
    return {
        "success": True,
        "module": "delivery",
        "message": "Delivery API is available"
    }
