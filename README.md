# ClientMeetMatic

A Windows/Outlook automation tool that turns a spreadsheet of clients into a real driving
route: it validates addresses and looks up live distances/travel times with the Google
Maps API, orders visits by priority and geography, and books back-to-back appointments
directly in Outlook Calendar — respecting business hours, lunch, and your existing
calendar.

## Features
- Reads a client list from Excel (`ClientName`, `Address`, `Priority`, optional `Duration`).
- Validates every address up front via the Geocoding API, so a typo is reported before
  any scheduling happens instead of failing mid-route.
- Visits clients in priority order (High → Medium → Low); within each priority tier,
  visits the geographically nearest remaining client next, instead of just file order.
- Looks up real driving distance/duration in batched Google Maps Distance Matrix calls
  (one call per stop covering all remaining candidates), with automatic retry on
  transient API errors.
- Books each appointment in Outlook Calendar with a 15-minute reminder, respecting
  business hours, a lunch window, and any appointments already on your calendar — clients
  that don't fit in the day are reported as unscheduled rather than booked at 9 PM.
- `--dry-run` mode previews the full route/schedule without touching Outlook.
- Logs every run to `%APPDATA%\ClientMeetMatic\logs\app.log` in addition to the console.
- Clear error messages for the most common failure points: a missing/invalid API key, a
  spreadsheet missing required columns or with bad Priority values, or Outlook not being
  installed/running.

## For Recruiters (no Python required)

1. Download `ClientMeetMatic.exe` (see [Building the executable](#building-the-executable)
   for how it's produced, or grab it from wherever your team distributes it).
2. Run it. On first launch you'll land on **Settings** — paste your Google Maps API key,
   pick your client list Excel file, and set your business hours/lunch window. This is
   saved for next time.
3. Click **Save & Continue** to see the **Route Preview** — the planned visiting order,
   distances, and start times. Double-click a row to change that client's priority.
4. Click **Book It** to create the appointments in Outlook. Results (and any failures)
   are shown per client.

You still need **Microsoft Outlook** installed and configured, and a **Google Maps API
key** with the Distance Matrix and Geocoding APIs enabled (get one from the
[Google Cloud Console](https://console.cloud.google.com/google/maps-apis)).

## For Developers

### Prerequisites
- **Windows** with **Microsoft Outlook** installed and configured (this project automates
  Outlook via COM through `pywin32`, so it will not run on macOS/Linux).
- **Python 3.9+**.
- A **Google Maps API key** with the *Distance Matrix API* and *Geocoding API* enabled.

### Setup

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
   (This is the developer-workflow config path; the packaged GUI instead stores settings
   in `%APPDATA%\ClientMeetMatic\config.json` — see `src/config.py`.)

3. Add your client data. Copy `Client List/Clients.sample.xlsx` to
   `Client List/Clients.xlsx` (this path is gitignored, so your real data is never
   committed) and fill in your own rows:
   - **ClientName** — name of the client.
   - **Address** — full address (used for the Google Maps lookup).
   - **Priority** — `High`, `Medium`, or `Low`.
   - **Duration** *(optional)* — meeting length in minutes for that client, overriding
     the default.

   The **first row** is treated as your starting location (e.g. your office), not a client
   to visit — see `Client List/Clients.sample.xlsx` for the expected format.

4. Run it:
   ```bash
   python -m src.main                 # plans and books tomorrow's route
   python -m src.main --dry-run       # preview only, no Outlook writes
   python -m src.main --date 2026-08-10 --duration 45 --file "Client List/Clients.xlsx"
   python -m src.main --set-priority "Acme Co" High   # update one client's priority
   ```
   Or launch the GUI directly from source:
   ```bash
   python -m src.gui.app
   ```

### Running the tests

The Google Maps and Outlook calls are mocked in the test suite, so tests run without a real
API key or Outlook installation:
```bash
pip install -r requirements.txt
pytest
```

## Building the executable

```bash
powershell -File scripts\build_exe.ps1
```

Produces a one-file, windowed `dist\ClientMeetMatic.exe` from `run_gui.py` via
`clientmeetmatic.spec`. The script creates an isolated `.venv-build` virtualenv
(containing only `requirements.txt` + `requirements-build.txt`) on first run and builds
from that — building against a Python install that also has unrelated packages on it can
make PyInstaller's dependency scanner hang for many minutes, or crash on a buggy hook for
a package you don't even use (see the comment in `clientmeetmatic.spec`). Smoke-test the
built `.exe` on a machine other than your dev machine before distributing it; COM
registration and bundled-DLL issues often only show up there.

## Troubleshooting
- **"No Google Maps API key configured"** — make sure `.env` exists (copied from
  `.env.example`, dev workflow) or the GUI Settings screen has a key saved, and that it's
  a real key.
- **"Could not validate the following address(es)"** — one or more addresses in your
  Excel file didn't resolve on Google Maps; fix the typo and re-run.
- **"Could not create the appointment in Outlook..."** — Outlook must be installed,
  configured with a mail profile, and (ideally) already running.
- **"missing required column(s)"** — your Excel file must have `ClientName`, `Address`,
  and `Priority` columns exactly as named.
- Check `%APPDATA%\ClientMeetMatic\logs\app.log` for a full run history if something
  failed and you didn't see why in the console/GUI.

## Known limitations
- Only driving distance/duration is supported (no walking/transit modes).
- Nearest-neighbor routing is a greedy heuristic within each priority tier, not a true
  shortest-route (TSP) solve — good enough for a day's stops, not optimal for large lists.
- No support for multi-day splitting if a client list doesn't fit in one business day;
  overflow clients are reported as unscheduled rather than carried to the next day.
