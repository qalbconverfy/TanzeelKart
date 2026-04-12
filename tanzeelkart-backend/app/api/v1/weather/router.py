from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.weather import schemas, service

router = APIRouter()


# ── ESP32 Data Receive ────────────────────
@router.post("/sensor-data")
async def receive_sensor_data(
    payload: schemas.SensorDataRequest,
    db: AsyncSession = Depends(get_db),
):
    return await service.receive_sensor_data(payload, db)


# ── Latest Weather ────────────────────────
@router.get("/latest")
async def get_latest_weather(
    node_id: str = Query("reoti_main"),
):
    return await service.get_latest_weather(node_id)


# ── Forecast ──────────────────────────────
@router.get("/forecast")
async def get_forecast(
    node_id: str = Query("reoti_main"),
):
    return await service.get_weather_forecast(node_id)


# ── Sensor Nodes ──────────────────────────
@router.get("/nodes")
async def get_sensor_nodes():
    return await service.get_sensor_nodes()
