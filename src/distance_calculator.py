import time

import googlemaps

TRANSIENT_STATUSES = {'OVER_QUERY_LIMIT', 'UNKNOWN_ERROR'}
MAX_RETRIES = 3
BACKOFF_SECONDS = 1


class DistanceLookupError(RuntimeError):
    pass


def _require_api_key(api_key):
    if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY':
        raise DistanceLookupError(
            "No Google Maps API key configured. Set GOOGLE_MAPS_API_KEY in your .env file."
        )


def _call_with_retry(func, **kwargs):
    """Retries transient Distance Matrix statuses and network errors with backoff."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            result = func(**kwargs)
        except Exception as exc:
            last_exc = exc
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_SECONDS * (2 ** attempt))
                continue
            raise DistanceLookupError(f"Google Maps API request failed: {exc}") from exc

        if result.get('status') in TRANSIENT_STATUSES and attempt < MAX_RETRIES - 1:
            time.sleep(BACKOFF_SECONDS * (2 ** attempt))
            continue
        return result

    raise DistanceLookupError("Google Maps API request failed after retries.") from last_exc


def get_distance_matrix(api_key, origin, destinations):
    """Returns [(destination, distance_text, duration_minutes), ...] for one origin to many
    destinations, in the same order as `destinations`, using a single batched API call."""
    _require_api_key(api_key)
    if not destinations:
        return []

    gmaps = googlemaps.Client(key=api_key)
    result = _call_with_retry(
        gmaps.distance_matrix, origins=[origin], destinations=destinations, mode='driving'
    )

    if result.get('status') != 'OK':
        raise DistanceLookupError(f"Google Maps API returned status: {result.get('status')}")

    elements = result['rows'][0]['elements']
    legs = []
    for destination, element in zip(destinations, elements):
        if element.get('status') != 'OK':
            raise DistanceLookupError(
                f"Could not find a driving route from '{origin}' to '{destination}' "
                f"(status: {element.get('status')})."
            )
        legs.append((
            destination,
            element['distance']['text'],
            round(element['duration']['value'] / 60),
        ))
    return legs


def get_distance_and_duration(api_key, origin, destination):
    """Returns (distance_text, duration_minutes) driving from origin to destination."""
    _, distance_text, duration_minutes = get_distance_matrix(api_key, origin, [destination])[0]
    return distance_text, duration_minutes


def calculate_distance(api_key, origin, destination):
    """Kept for backwards compatibility: returns just the distance text."""
    distance_text, _ = get_distance_and_duration(api_key, origin, destination)
    return distance_text
