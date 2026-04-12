from app.core.config import settings
from app.api.v1.videos.schemas import (
    VideoSearchRequest,
    VideoResponse,
    VideoListResponse,
    VideoCategory
)
from app.core.exceptions import ValidationException
from loguru import logger
import httpx


# ─────────────────────────────────────────
# YouTube API Base URL
# ─────────────────────────────────────────

YOUTUBE_BASE = "https://www.googleapis.com/youtube/v3"

# Default categories for TanzeelKart
DEFAULT_CATEGORIES = [
    VideoCategory(
        name="Kheti Baari",
        query="kheti baari UP kisan",
        icon="🌾"
    ),
    VideoCategory(
        name="Mausam",
        query="mausam UP ballia weather",
        icon="🌤️"
    ),
    VideoCategory(
        name="Mandi Bhav",
        query="mandi bhav sabzi rate today UP",
        icon="💰"
    ),
    VideoCategory(
        name="Fasal Tips",
        query="fasal tips hindi kisan",
        icon="🌱"
    ),
    VideoCategory(
        name="Pashu Palan",
        query="pashu palan dairy farming hindi",
        icon="🐄"
    ),
    VideoCategory(
        name="Government Schemes",
        query="kisan yojana PM kisan UP",
        icon="🏛️"
    ),
]


# ─────────────────────────────────────────
# Search Videos
# ─────────────────────────────────────────

async def search_videos(
    payload: VideoSearchRequest,
) -> VideoListResponse:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{YOUTUBE_BASE}/search",
                params={
                    "key": settings.YOUTUBE_API_KEY,
                    "q": payload.query,
                    "part": "snippet",
                    "type": "video",
                    "maxResults": payload.max_results,
                    "relevanceLanguage": payload.language,
                    "regionCode": "IN",
                    "order": "relevance",
                },
                timeout=10.0
            )
            data = response.json()

            if "error" in data:
                logger.error(f"YouTube API error: {data}")
                raise ValidationException(
                    "Video search failed"
                )

            videos = []
            for item in data.get("items", []):
                snippet = item.get("snippet", {})
                video_id = item["id"].get("videoId", "")
                videos.append(VideoResponse(
                    video_id=video_id,
                    title=snippet.get("title", ""),
                    description=snippet.get("description", ""),
                    thumbnail=snippet.get(
                        "thumbnails", {}
                    ).get("high", {}).get("url", ""),
                    channel_name=snippet.get(
                        "channelTitle", ""
                    ),
                    published_at=snippet.get(
                        "publishedAt", ""
                    ),
                    view_count=None,
                    duration=None,
                    url=f"https://youtube.com/watch?v={video_id}"
                ))

            return VideoListResponse(
                videos=videos,
                total=len(videos),
                query=payload.query
            )

    except httpx.TimeoutException:
        raise ValidationException("YouTube API timeout")
    except Exception as e:
        logger.error(f"Video search error: {e}")
        raise ValidationException("Video search failed")


# ─────────────────────────────────────────
# Get Video Categories
# ─────────────────────────────────────────

async def get_categories() -> list:
    return [
        {
            "name": cat.name,
            "query": cat.query,
            "icon": cat.icon
        }
        for cat in DEFAULT_CATEGORIES
    ]


# ─────────────────────────────────────────
# Get Videos By Category
# ─────────────────────────────────────────

async def get_videos_by_category(
    category_name: str,
    max_results: int = 10,
) -> VideoListResponse:
    # Category dhundo
    category = next(
        (c for c in DEFAULT_CATEGORIES
         if c.name.lower() == category_name.lower()),
        None
    )

    if not category:
        raise ValidationException("Category not found")

    return await search_videos(
        VideoSearchRequest(
            query=category.query,
            max_results=max_results
        )
    )


# ─────────────────────────────────────────
# Get Trending Farm Videos
# ─────────────────────────────────────────

async def get_trending_videos() -> VideoListResponse:
    return await search_videos(
        VideoSearchRequest(
            query="kisan kheti UP ballia 2026",
            max_results=20
        )
    )
