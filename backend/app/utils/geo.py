import math

EARTH_RADIUS_KM = 6371.0088


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in kilometres."""
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def search_radius_km(
    center_lat: float,
    center_lon: float,
    bounding_box: list[float] | None,
    min_radius_km: float = 50.0,
    margin_km: float = 25.0,
) -> float:
    """Radius within which a generated attraction is plausibly 'in' the destination.

    Uses the geocoder's bounding box ([min_lat, max_lat, min_lon, max_lon]) so a
    country-level query ("Japan") gets a country-sized radius, while a city query
    ("Kyoto") stays tight. Falls back to `min_radius_km` without a box.
    """
    radius = min_radius_km
    if bounding_box and len(bounding_box) == 4:
        min_lat, max_lat, min_lon, max_lon = bounding_box
        corners = [(min_lat, min_lon), (min_lat, max_lon), (max_lat, min_lon), (max_lat, max_lon)]
        farthest = max(haversine_km(center_lat, center_lon, la, lo) for la, lo in corners)
        radius = max(radius, farthest + margin_km)
    return radius
