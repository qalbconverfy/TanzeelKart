from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Shops root")
async def shops_root():
    return {
        "success": True,
        "module": "shops",
        "message": "Shops API is available"
    }
