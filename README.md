# Fähr-Radar Linz

Home Assistant custom integration for the **St. Johannes** and **Linz Remagen** ferries between Linz am Rhein and Remagen-Kripp.

The integration creates one human-readable status sensor per ferry. Every original field returned by the API is exposed unchanged as a sensor attribute, alongside the calculated `eta_minutes` value. The sensors are designed for dashboards, automations and voice assistants such as Siri.

## Features

- Tracks **ST. JOHANNES** and **LINZ REMAGEN** independently.
- Creates a separate device and status sensor for each ferry.
- Spoken status with location, direction and estimated arrival when available.
- Exposes all original API fields as attributes, including fields whose value is `null`.
- Adds the calculated `eta_minutes` attribute.
- Refreshes both ferries in one API request every 10 seconds.
- If one ferry is temporarily missing from the API response, its sensor remains available with an explanatory status.
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

## Entities

The integration creates:
- A status sensor for **Fähre St. Johannes**.
- A status sensor for **Fähre Linz Remagen**.

Each sensor's state contains the spoken status. Its attributes contain the original API response fields and the calculated `eta_minutes` value.

## Data source

Ferry information is retrieved from the public API at [faehr-radar-linz.de](https://faehr-radar-linz.de/).

This is an independent community integration and is not affiliated with the ferry operator or the website.
