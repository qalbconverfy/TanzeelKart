from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_udhaar():
    return {"message": "Udhaar API - Coming Soon"}
    