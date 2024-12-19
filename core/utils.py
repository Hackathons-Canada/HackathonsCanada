import logging
from typing import Optional, Tuple

import requests
from django.conf import settings
from django.core.cache import cache
from requests import RequestException


logger = logging.getLogger(__name__)


def unreviewed_hackathons(request) -> str:
    from core.models import Hackathon, ReviewStatus

    """Returns count of all hackathons that haven't yet been reviewed."""
    unreviewed_hackathons_count: int = Hackathon.objects.filter(
        review_status=ReviewStatus.Pending
    ).count()
    if unreviewed_hackathons_count == 0:
        return ""  # No unreviewed hackathons, no need to display anything
    return str(unreviewed_hackathons_count)


def get_coordinates(city: str, country: str) -> Optional[Tuple[float, float]]:
    # todo: overwrite with the location retried from the browser
    """
    Get coordinates for a city and country using Nominatim OpenStreetMap API with caching
    Returns (latitude, longitude) tuple or None if geocoding fails
    """
    cache_key = f"geocode_{city}_{country}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result

    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"city": city, "country": country, "format": "json", "limit": 1}
        headers = {
            "User-Agent": f"Hackathon's Canada: a hackathon Platform ({settings.SITE_URL})"
        }
        # todo: redo with a async request
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()

        results = response.json()

        if results:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            coordinates = (lat, lon)

            # Cache for 30 days
            cache.set(cache_key, coordinates, timeout=60 * 60 * 24 * 30)

            return coordinates

    except (RequestException, ValueError, KeyError, IndexError) as e:
        logger.error(f"Geocoding failed for {city}, {country}: {str(e)}", exc_info=True)

    return None
