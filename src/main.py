import os
from src.excel_handler import read_excel, add_priority, save_excel
from src.distance_calculator import calculate_distance
from src.scheduler import schedule_appointment

EXCEL_FILE = 'data/clients.xlsx'
API_KEY = 'YOUR_GOOGLE_MAPS_API_KEY'

def main():
    df = read_excel(EXCEL_FILE)
    origin = df.iloc[0]['Address']
    for i, row in df.iterrows():
        if i == 0:
            continue
        destination = row['Address']
        distance = calculate_distance(API_KEY, origin, destination)
        print(f"Distance from {origin} to {destination}: {distance}")
        
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
