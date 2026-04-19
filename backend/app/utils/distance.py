import math


def haversine(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
) -> float:
    """Returns distance in km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2 +
        math.cos(math.radians(lat1)) *
        math.cos(math.radians(lat2)) *
        math.sin(dlon / 2) ** 2
    )
    return R * 2 * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )


def is_within_radius(
    lat1: float, lon1: float,
    lat2: float, lon2: float,
    radius_km: float,
) -> bool:
    return haversine(lat1, lon1, lat2, lon2) <= radius_km
