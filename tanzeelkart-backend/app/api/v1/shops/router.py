from fastapi import APIRouter
router = APIRouter()

@router.get("/")
async def get_shops():
    return {"message": "Shops API - Coming Soon"}
    