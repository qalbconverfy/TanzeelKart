from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SensorDataRequest(BaseModel):
    node_id: str
    temperature: float
    humidity: float
    pressure: Optional[float] = None
    rainfall: Optional[float] = None
    soil_moisture: Optional[float] = None
    wind_speed: Optional[float] = None
    api_key: str


class WeatherResponse(BaseModel):
    node_id: str
    location_name: Optional[str]
    temperature: float
    humidity: float
    pressure: Optional[float]
    rainfall: Optional[float]
    soil_moisture: Optional[float]
    wind_speed: Optional[float]
    recorded_at: datetime
    advice: Optional[str]


class WeatherForecastResponse(BaseModel):
    location: str
    current: WeatherResponse
    forecast_24h: str
    forecast_48h: str
    forecast_72h: str
    crop_advice: str
    rain_probability: float


class SensorNodeResponse(BaseModel):
    node_id: str
    location_name: str
    latitude: float
    longitude: float
    is_active: bool
    last_reading: Optional[datetime]
    battery_level: Optional[float]
