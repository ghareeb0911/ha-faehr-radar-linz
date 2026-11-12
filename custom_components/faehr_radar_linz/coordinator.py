"""Fetch and prepare ferry data."""

from __future__ import annotations

from datetime import datetime, time, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_URL, FERRY_NAME, SCAN_INTERVAL


def _ferry_from_payload(payload: object) -> dict:
    """Find the St. Johannes entry in the API response."""
    candidates = payload
    if isinstance(payload, dict):
        for key in ("ferries", "data", "items"):
            if isinstance(payload.get(key), list):
                candidates = payload[key]
                break
        else:
            candidates = [payload]

    if not isinstance(candidates, list):
        raise UpdateFailed("Unerwartetes Datenformat der Fähr-Radar-API")

    for item in candidates:
        if not isinstance(item, dict):
            continue
        name = str(item.get("ship_name", item.get("name", ""))).strip().upper()
        if name == FERRY_NAME:
            return item

    raise UpdateFailed(f"Fähre {FERRY_NAME} wurde in der API-Antwort nicht gefunden")


def _eta_minutes(eta_value: object) -> int | None:
    """Convert an API time value (HH:MM[:SS]) into minutes from now."""
    if not eta_value:
        return None

    now = datetime.now().astimezone()
    try:
        if isinstance(eta_value, (int, float)):
            eta = datetime.fromtimestamp(float(eta_value), tz=now.tzinfo)
        else:
            raw = str(eta_value).strip()
            try:
                eta = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                if eta.tzinfo is None:
                    eta = eta.replace(tzinfo=now.tzinfo)
            except ValueError:
                parsed_time = time.fromisoformat(raw)
                eta = datetime.combine(now.date(), parsed_time, tzinfo=now.tzinfo)
                if (eta - now).total_seconds() < -120:
                    eta += timedelta(days=1)
        return max(0, round((eta - now).total_seconds() / 60))
    except (TypeError, ValueError, OverflowError):
        return None


def _prepare_data(ferry: dict) -> dict:
    """Create a compact, presentation-ready sensor payload."""
    status = str(ferry.get("movement_state", ferry.get("status", "unknown"))).strip().upper()
    next_dock = ferry.get("next_dock")
    last_dock = ferry.get("last_dock")
    stationary_location = ferry.get("stationary_location")

    eta_value = None
    if next_dock:
        for suffix in ("a", "b"):
            dock_name = ferry.get(f"eta_dock_{suffix}_name")
            if dock_name and str(dock_name).casefold() == str(next_dock).casefold():
                eta_value = ferry.get(f"eta_dock_{suffix}")
                break
    if eta_value is None:
        eta_value = ferry.get("eta_dock_a") or ferry.get("eta_dock_b")

    minutes = _eta_minutes(eta_value)
    if minutes is None:
        eta_text = "der Zeitpunkt ist noch unbekannt"
    elif minutes == 0:
        eta_text = "in wenigen Augenblicken"
    elif minutes == 1:
        eta_text = "in 1 Minute"
    else:
        eta_text = f"in {minutes} Minuten"

    if status in ("STATIONARY", "STOPPED", "STILL"):
        location = str(stationary_location or "").replace("at ", "").strip()
        if not location:
            location = str(last_dock or "unbekannt")
        if next_dock:
            message = (
                f"Wartet in {location}. Voraussichtliche Ankunft in "
                f"{next_dock} {eta_text}."
            )
        else:
            message = f"Wartet in {location}. Das nächste Ziel ist noch unbekannt."
    elif status in ("MOVING", "IN_MOTION", "UNDERWAY"):
        route = f"von {last_dock} " if last_dock else ""
        destination = str(next_dock or "unbekannt")
        message = (
            f"Unterwegs {route}nach {destination}. "
            f"Voraussichtliche Ankunft in {destination} {eta_text}."
        )
    else:
        message = f"Fährstatus derzeit nicht verfügbar ({status.lower()})."

    return {
        "message": message,
        "ship_name": ferry.get("ship_name", FERRY_NAME),
        "movement_state": status.lower(),
        "stationary_location": stationary_location,
        "next_dock": next_dock,
        "last_dock": last_dock,
        "eta_minutes": minutes,
        "speed_knots": ferry.get("speed_knots"),
        "dock_distance_meters": ferry.get("dock_distance_meters"),
        "timestamp_formatted": ferry.get("timestamp_formatted"),
    }


class FerryDataUpdateCoordinator(DataUpdateCoordinator[dict]):
    """Coordinate API updates."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            logger=__import__("logging").getLogger(__name__),
            name="Fähr-Radar Linz",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict:
        """Fetch the ferry data."""
        try:
            async with self.session.get(API_URL, timeout=aiohttp.ClientTimeout(total=15)) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Fährdaten: {err}") from err

        ferry = _ferry_from_payload(payload)
        return _prepare_data(ferry)
