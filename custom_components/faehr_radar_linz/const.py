"""Constants for the Fährinformation Linz/Kripp integration."""

from datetime import timedelta

# Keep the internal domain stable so existing Home Assistant installations
# can upgrade without removing and re-adding the integration.
DOMAIN = "faehr_radar_linz"
# Official public API used strictly as the integration data source.
API_URL = "https://faehr-radar-linz.de/api/ferries"
FERRIES = {
    "ST. JOHANNES": {
        "device_id": "st_johannes",
        "device_name": "Fähre St. Johannes",
    },
    "LINZ-REMAGEN": {
        "device_id": "linz_remagen",
        "device_name": "Fähre Linz Remagen",
    },
}
SCAN_INTERVAL = timedelta(seconds=10)
