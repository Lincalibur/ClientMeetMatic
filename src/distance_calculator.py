import openrouteservice

def geocode(api_key, address):
    """
    Geocode an address to latitude and longitude coordinates.
    
    :param api_key: Your OpenRouteService API key.
    :param address: The address to geocode.
    :return: A tuple of (latitude, longitude).
    """
    client = openrouteservice.Client(key=api_key)
    try:
        # Perform geocoding
        geocode = client.pelias_search(text=address)
        # Extract coordinates from the response
        coordinates = geocode['features'][0]['geometry']['coordinates']
        return coordinates[1], coordinates[0]  # Return as (latitude, longitude)
    except openrouteservice.exceptions.ApiError as e:
        print(f"Geocoding API Error: {e}")
        return None, None

def calculate_distance(api_key, origin, destination):
    """
    Calculate the driving distance between two coordinates.
    
    :param api_key: Your OpenRouteService API key.
    :param origin: The origin coordinates as (latitude, longitude).
    :param destination: The destination coordinates as (latitude, longitude).
    :return: The distance in kilometers.
    """
    client = openrouteservice.Client(key=api_key)
    
    # Ensure coordinates are in [longitude, latitude] format
    coordinates = [origin, destination]
    
    try:
        # Request directions
        routes = client.directions(coordinates=coordinates, profile='driving-car', format='geojson')
        # Extract distance from the response
        distance = routes['features'][0]['properties']['segments'][0]['distance']
        # Convert meters to kilometers for easier reading
        return f"{distance / 1000:.2f} km"
    except openrouteservice.exceptions.ApiError as e:
        print(f"Distance API Error: {e}")
        return None
