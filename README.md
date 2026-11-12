# Fähr-Radar Linz

Home Assistant custom integration for the **St. Johannes** ferry between Linz am Rhein and Remagen-Kripp.

The integration creates one human-readable sensor with the current ferry status and estimated arrival time. It is designed for dashboards, automations and voice assistants such as Siri.

## Features

- Tracks **ST. JOHANNES** specifically (not the other ferry).
- One spoken-status sensor, for example:  
  `Wartet in Linz. Voraussichtliche Ankunft in Kripp in 8 Minuten.`
- Reports whether the ferry is stationary or moving, its location/direction and estimated arrival.
- Refreshes data every 10 seconds.
- No API key or account required.
- No dashboard card or map required.

## Installation via HACS

Until the integration is included in the HACS default store:

1. Open **HACS** in Home Assistant.
2. Open the three-dot menu and select **Custom repositories**.
3. Add `https://github.com/ghareeb0911/ha-faehr-radar-linz` as an **Integration**.
4. Find **Fähr-Radar Linz** in HACS and install it.
5. Restart Home Assistant.
6. Go to **Settings → Devices & services → Add integration**.
7. Search for **Fähr-Radar Linz** and add it.

## Entity

The integration creates a text sensor for the spoken status. Its attributes also expose structured details such as movement state, next dock, last dock and ETA in minutes.

## Data source

Ferry information is retrieved from the public API at [faehr-radar-linz.de](https://faehr-radar-linz.de/).

This is an independent community integration and is not affiliated with the ferry operator or the website.

## Development status

This is an initial release candidate. API response handling and Home Assistant compatibility should be verified against a live instance before submitting the project to the HACS default repository.
