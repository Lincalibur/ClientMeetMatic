import time

import googlemaps

MAX_RETRIES = 3
BACKOFF_SECONDS = 1


class AddressValidationError(RuntimeError):
    pass


def validate_addresses(api_key, addresses):
    """Checks that each address geocodes to a real location. Returns the subset of
    `addresses` that failed to resolve (empty list if all are valid), so callers can
    report every bad address at once instead of failing mid-route on the first one."""
    if not api_key or api_key == 'YOUR_GOOGLE_MAPS_API_KEY':
        raise AddressValidationError(
            "No Google Maps API key configured. Set GOOGLE_MAPS_API_KEY in your .env file."
        )

    gmaps = googlemaps.Client(key=api_key)
    return [address for address in addresses if not _resolves(gmaps, address)]


def _resolves(gmaps, address):
    for attempt in range(MAX_RETRIES):
        try:
            return bool(gmaps.geocode(address))
        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep(BACKOFF_SECONDS * (2 ** attempt))
                continue
            return False
