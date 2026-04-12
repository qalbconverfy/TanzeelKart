from pydantic import BaseModel
from typing import Optional, List


class MapLocationRequest(BaseModel):
    name: str
    latitude: float
    longitude: float
    category: str
    description: Optional[str] = None
    address: Optional[str] = None


class MapLocationResponse(BaseModel):
    id: str
    name: str
    latitude: float
    longitude: float
    category: str
    description: Optional[str]
    address: Optional[str]
    weather_node_id: Optional[str]


class MapDataResponse(BaseModel):
    shops: List[dict]
    weather_nodes: List[dict]
    landmarks: List[dict]
    center_latitude: float
    center_longitude: float
    zoom_level: int
