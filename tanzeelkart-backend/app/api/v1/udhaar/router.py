from fastapi import APIRouter

router = APIRouter()


@router.get("/", summary="Udhaar root")
async def udhaar_root():
    return {
        "success": True,
        "module": "udhaar",
        "message": "Udhaar API is available"
    }
