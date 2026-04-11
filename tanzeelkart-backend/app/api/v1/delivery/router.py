from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_delivery():
    return {"message": "Delivery API - Coming Soon"}
    