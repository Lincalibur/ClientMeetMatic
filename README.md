# ClientMeetMatic

This project calculates distances between clients using Google Maps and schedules appointments in Outlook based on distance and priority.

## Features
- Calculate distances between client addresses using Google Maps.
- Prioritize clients and schedule appointments in Outlook Calendar.
- User-friendly setup with minimal interaction with the code.

## Prerequisites
1. **Python**: Ensure Python is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).
2. **Google Maps API Key**: Obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/).
3. **Microsoft Outlook**: Ensure Microsoft Outlook is installed and configured on your system.

## Setup Instructions

### Step 1: Download and Extract the Project
1. Download the project from the [GitHub repository](https://github.com/yourusername/ClientDistanceScheduler) (replace with your actual GitHub repository link).
2. Extract the downloaded ZIP file to a desired location on your computer.

### Step 2: Prepare the Excel File
1. Open the `clients.xlsx` file located in the `data` directory.
2. Add your client information in the following format:
   - **ClientName**: Name of the client.
   - **Address**: Full address of the client.
   - **Priority**: Priority of the client (e.g., High, Medium, Low).
3. Save and close the Excel file.

### Step 3: Install Required Packages
1. Open a terminal or command prompt.
2. Navigate to the project directory:
   ```bash
   cd path/to/ClientMeetMatic
