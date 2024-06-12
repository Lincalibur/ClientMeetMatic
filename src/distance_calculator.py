import googlemaps

def calculate_distance(api_key, origin, destination):
    gmaps = googlemaps.Client(key=api_key)
    result = gmaps.distance_matrix(origins=[origin], destinations=[destination], mode='driving')
    return result['rows'][0]['elements'][0]['distance']['text']
