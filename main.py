import sys
import os
from datetime import datetime, timedelta

from src.excel_handler import read_excel
from src.distance_calculator import calculate_distance, geocode
from src.scheduler import schedule_appointment
from src.waze_url_generator import generate_waze_url

EXCEL_FILE = 'data/Clients.xlsx'
API_KEY = 'ac603383f8174be282c3442f547e436f'  # Replace with your OpenCage API key

MAX_MEETINGS_PER_DAY = 3
INITIAL_RADIUS_KM = 50
RADIUS_INCREMENT_KM = 50

def filter_clients_within_radius(df, origin, radius_km):
    filtered_clients = []
    for i, row in df.iterrows():
        destination_address = row['Address']
        destination = geocode(API_KEY, destination_address)
        if destination == (None, None):
            continue
        distance = calculate_distance(API_KEY, origin, destination)
        if distance and float(distance.split()[0]) <= radius_km:
            filtered_clients.append((row, destination))
    return filtered_clients

def main():
    df = read_excel(EXCEL_FILE)
    origin_address = df.iloc[0]['Address']
    origin = geocode(API_KEY, origin_address)
    if origin == (None, None):
        print(f"Failed to geocode origin address: {origin_address}")
        return
    
    start_date = datetime.strptime("2024-06-10", "%Y-%m-%d")
    day_meetings = 0
    current_date = start_date
    radius_km = INITIAL_RADIUS_KM
    index = 0
    
    while index < len(df):
        if day_meetings == MAX_MEETINGS_PER_DAY:
            current_date += timedelta(days=1)
            day_meetings = 0
            radius_km = INITIAL_RADIUS_KM  # Reset radius for next day
        
        filtered_clients = filter_clients_within_radius(df[index:], origin, radius_km)
        
        if not filtered_clients:
            radius_km += RADIUS_INCREMENT_KM
            continue
        
        for row, destination in filtered_clients[:MAX_MEETINGS_PER_DAY - day_meetings]:
            distance = calculate_distance(API_KEY, origin, destination)
            if distance is None:
                continue
            
            destination_address = row['Address']
            print(f"Distance from {origin_address} to {destination_address}: {distance}")
            
            # Generate Waze URL for navigation
            waze_url = generate_waze_url(destination_address)
            print(f"Navigate using Waze: {waze_url}")
            
            # Schedule appointment based on distance and priority
            schedule_appointment(
                subject=f"Meeting with {row['ClientName']}",
                start_time=current_date.strftime("%Y-%m-%d") + " 10:00",
                duration=60,
                location=row['Address'],
                body=f"Discuss with {row['ClientName']}"
            )
            
            day_meetings += 1
            index += 1
            if day_meetings == MAX_MEETINGS_PER_DAY:
                break
        
        if day_meetings < MAX_MEETINGS_PER_DAY:
            index += len(filtered_clients)

if __name__ == "__main__":
    main()
