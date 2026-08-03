# ClientMeetMatic

A Windows/Outlook automation tool that turns a spreadsheet of clients into a real driving
route: it looks up live distances and travel times between addresses with the Google Maps
Distance Matrix API, orders visits by priority, and books back-to-back appointments directly
in Outlook Calendar — spaced out to account for actual travel time between stops.

## Features
- Reads a client list from Excel (`ClientName`, `Address`, `Priority`).
- Looks up real driving distance and duration between consecutive stops via the Google Maps
  Distance Matrix API.
- Visits clients in priority order (High → Medium → Low), starting from a fixed origin
  (e.g. your office — the first row in the spreadsheet).
- Books each appointment in Outlook Calendar with a 15-minute reminder, scheduled
  back-to-back and spaced out by meeting length + travel time from the previous stop.
- Clear error messages for the most common failure points: a missing/invalid API key, a
  spreadsheet missing required columns or with bad Priority values, or Outlook not being
  installed/running.

## Prerequisites
- **Windows** with **Microsoft Outlook** installed and configured (this project automates
  Outlook via COM through `pywin32`, so it will not run on macOS/Linux).
- **Python 3.9+**.
- A **Google Maps API key** with the *Distance Matrix API* enabled — get one from the
  [Google Cloud Console](https://console.cloud.google.com/google/maps-apis).

## Setup

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/Lincalibur/ClientMeetMatic.git
   cd ClientMeetMatic
   pip install -r requirements.txt
   ```

2. Configure your API key:
   ```bash
   copy .env.example .env
   ```
   Then edit `.env` and set `GOOGLE_MAPS_API_KEY` to your real key. Never commit `.env`.

3. Add your client data. Copy `Client List/Clients.sample.xlsx` to
   `Client List/Clients.xlsx` (this path is gitignored, so your real data is never
   committed) and fill in your own rows:
   - **ClientName** — name of the client.
   - **Address** — full address (used for the Google Maps lookup).
   - **Priority** — `High`, `Medium`, or `Low`.

   The **first row** is treated as your starting location (e.g. your office), not a client
   to visit — see `Client List/Clients.sample.xlsx` for the expected format.

4. Run it:
   ```bash
   python -m src.main
   ```
   This prints the planned route (distance/travel time from the previous stop, and the
   scheduled start time for each visit) and creates the corresponding appointments in your
   default Outlook calendar, starting the next day at 9:00 AM.

## Running the tests

The Google Maps and Outlook calls are mocked in the test suite, so tests run without a real
API key or Outlook installation:
```bash
pip install -r requirements.txt
pytest
```

## Troubleshooting
- **"No Google Maps API key configured"** — make sure `.env` exists (copied from
  `.env.example`) and `GOOGLE_MAPS_API_KEY` is set to a real key.
- **"Could not create the appointment in Outlook..."** — Outlook must be installed,
  configured with a mail profile, and (ideally) already running.
- **"missing required column(s)"** — your Excel file must have `ClientName`, `Address`,
  and `Priority` columns exactly as named.

## Known limitations
- Scheduling doesn't account for business hours/lunch breaks beyond a fixed 9:00 AM start
  — long routes can run into the evening.
- Only driving distance/duration is supported (no walking/transit modes).
