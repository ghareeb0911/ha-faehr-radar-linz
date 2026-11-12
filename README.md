# Fähr-Radar Linz

Home Assistant custom integration for the **St. Johannes** and **Linz Remagen** ferries between Linz am Rhein and Remagen-Kripp.

## Features

- Tracks **ST. JOHANNES** and **LINZ REMAGEN** independently, with one Home Assistant device per ferry.
- Provides a spoken status sensor with location, direction and estimated arrival.
- Exposes the original API response fields as attributes on the status sensor, including fields whose value is `null`.
- Also creates individual entities for the most useful API values: movement/API status, location, last/next dock, dock names and ETAs, ETA minutes, speed, course, distance to dock, progress, timestamps, MMSI, coordinates and dock-presence flags.
- Publishes speed in both original knots and converted km/h (`knots × 1.852`).
- Missing values remain `unknown`/unavailable instead of being shown as zero.
- Refreshes both ferries in one API request every 10 seconds.
- If one ferry is temporarily missing from the API response, its status sensor remains available with an explanatory status.
- No API key or account required. No dashboard card or map required.

## Installation via HACS

Until the integration is included in the HACS default store:

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/ghareeb0911/ha-faehr-radar-linz` as an **Integration**.
4. Find **Fähr-Radar Linz** in HACS and install it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration**.
7. Search for **Fähr-Radar Linz** and add it.

## Entities

The integration creates a status entity and individual data entities for each ferry. All entities belonging to a ferry are grouped under that ferry's device. The status entity retains the complete API data as attributes for advanced use.

## Data source

Ferry information is retrieved from the public API at [faehr-radar-linz.de](https://faehr-radar-linz.de/).

This is an independent community integration and is not affiliated with the ferry operator or the website.
