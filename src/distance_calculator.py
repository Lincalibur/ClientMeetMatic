import pandas as pd
from geopy.distance import geodesic
from opencage.geocoder import OpenCageGeocode
import time

def geocode(api_key, address, retries=3, backoff_factor=0.3):
    """
    Geocode an address to latitude and longitude coordinates using OpenCage Geocoder with retries.
    
    :param api_key: OpenCage API key.
    :param address: The address to geocode.
    :param retries: Number of retry attempts.
    :param backoff_factor: Factor by which the delay is increased after each retry.
    :return: A tuple of (latitude, longitude).
    """
    geocoder = OpenCageGeocode(api_key)
    for attempt in range(retries):
        try:
            result = geocoder.geocode(address)
            if result and len(result):
                return result[0]['geometry']['lat'], result[0]['geometry']['lng']
        except Exception as e:
            print(f"Geocoding Error: {e}")
            if attempt < retries - 1:
                sleep_time = backoff_factor * (2 ** attempt)
                print(f"Retrying in {sleep_time:.1f} seconds...")
                time.sleep(sleep_time)
    return None, None

def calculate_distance(api_key, origin, destination):
    """
    Calculate the driving distance between two coordinates using geopy.
    
    :param api_key: Not used in this function, included for compatibility.
    :param origin: The origin coordinates as (latitude, longitude).
    :param destination: The destination coordinates as (latitude, longitude).
    :return: The distance in kilometers.
    """
    try:
        distance = geodesic(origin, destination).kilometers
        return f"{distance:.2f} km"
    except Exception as e:
        print(f"Distance Calculation Error: {e}")
        return None

def read_excel(file_path):
    return pd.read_excel(file_path)

def add_priority(df, client_name, priority):
    df.loc[df['ClientName'] == client_name, 'Priority'] = priority

def save_excel(df, file_path):
    df.to_excel(file_path, index=False)
