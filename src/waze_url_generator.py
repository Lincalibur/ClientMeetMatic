# src/waze_url_generator.py

def generate_waze_url(destination):
    base_url = "https://waze.com/ul"
    url = f"{base_url}?q={destination}&navigate=yes"
    return url
