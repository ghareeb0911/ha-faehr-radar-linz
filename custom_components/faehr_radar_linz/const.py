"""Constants for the Fähr-Radar Linz integration."""

from datetime import timedelta

DOMAIN = "faehr_radar_linz"
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
