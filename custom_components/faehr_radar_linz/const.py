"""Constants for the Fähr-Radar Linz integration."""

from datetime import timedelta

DOMAIN = "faehr_radar_linz"
API_URL = "https://faehr-radar-linz.de/api/ferries"
FERRY_NAME = "ST. JOHANNES"
SCAN_INTERVAL = timedelta(seconds=10)
