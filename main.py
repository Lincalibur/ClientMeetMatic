import sys
import os

from src.excel_handler import read_excel
from src.distance_calculator import calculate_distance,geocode
from src.scheduler import schedule_appointment
from src.waze_url_generator import generate_waze_url

EXCEL_FILE = 'data\Clients.xlsx'
API_KEY = '5b3ce3597851110001cf624868debe08e24b443e9454922fd3d5c933'

def main():
    df = read_excel(EXCEL_FILE)
    origin_address = df.iloc[0]['Address']
    origin = geocode(API_KEY, origin_address)
    for i, row in df.iterrows():
        if i == 0:
            continue
        destination_address = row['Address']
        destination = geocode(API_KEY, destination_address)
        distance = calculate_distance(API_KEY, origin, destination)
        print(f"Distance from {origin_address} to {destination_address}: {distance}")
        
        # Generate Waze URL for navigation
        waze_url = generate_waze_url(destination_address)
        print(f"Navigate using Waze: {waze_url}")
        
        # Schedule appointment based on distance and priority
        if row['Priority'] == 'High':
            schedule_appointment(
                subject=f"Meeting with {row['ClientName']}",
                start_time="2024-06-10 10:00",
                duration=60,
                location=row['Address'],
                body=f"Discuss with {row['ClientName']}"
            )
        origin = destination

if __name__ == "__main__":
    main()
