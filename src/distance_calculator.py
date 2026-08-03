import googlemaps


class DistanceLookupError(RuntimeError):
    pass


def get_distance_and_duration(api_key, origin, destination):
    """Returns (distance_text, duration_minutes) driving from origin to destination."""
    if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY':
        raise DistanceLookupError(
            "No Google Maps API key configured. Set GOOGLE_MAPS_API_KEY in your .env file."
        )

    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode='driving')

    if result.get('status') != 'OK':
        raise DistanceLookupError(f"Google Maps API returned status: {result.get('status')}")

    element = result['rows'][0]['elements'][0]
    if element.get('status') != 'OK':
        raise DistanceLookupError(
            f"Could not find a driving route from '{origin}' to '{destination}' "
            f"(status: {element.get('status')})."
        )

    distance_text = element['distance']['text']
    duration_minutes = round(element['duration']['value'] / 60)
    return distance_text, duration_minutes


def calculate_distance(api_key, origin, destination):
    """Kept for backwards compatibility: returns just the distance text."""
    distance_text, _ = get_distance_and_duration(api_key, origin, destination)
    return distance_text
