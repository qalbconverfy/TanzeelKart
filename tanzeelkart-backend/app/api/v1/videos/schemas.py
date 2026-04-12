from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime


class VideoSearchRequest(BaseModel):
    query: str
    max_results: Optional[int] = 10
    language: Optional[str] = "hi"

    @field_validator("max_results")
    @classmethod
    def validate_max(cls, v):
        if v < 1 or v > 50:
            raise ValueError("Max results 1-50")
        return v


class VideoResponse(BaseModel):
    video_id: str
    title: str
    description: Optional[str]
    thumbnail: str
    channel_name: str
    published_at: str
    view_count: Optional[str]
    duration: Optional[str]
    url: str


class VideoListResponse(BaseModel):
    videos: List[VideoResponse]
    total: int
    query: str


class VideoCategory(BaseModel):
    name: str
    query: str
    icon: str
