"""Fetch and prepare data for all ferries."""

from __future__ import annotations

import logging
from datetime import datetime, time, timedelta

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import API_URL, FERRIES, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


def _normalize_ferry_name(name: object) -> str:
    """Normalize a ferry name for matching despite spaces or punctuation."""
    return "".join(character for character in str(name).upper() if character.isalnum())


def _ferries_from_payload(payload: object) -> dict[str, dict]:
    """Return all configured ferries found in the API response."""
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

    ferries = {}
    for item in candidates:
        if not isinstance(item, dict):
            continue
        name = _normalize_ferry_name(item.get("ship_name", item.get("name", "")))
        configured_name = next(
            (
                ferry_name
                for ferry_name in FERRIES
                if _normalize_ferry_name(ferry_name) == name
            ),
            None,
        )
        if configured_name:
            ferries[configured_name] = item

    return ferries


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
    """Preserve API fields and add the spoken message and calculated ETA."""
    status = str(
        ferry.get("movement_state", ferry.get("status", "unknown"))
    ).strip().upper()
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
    elif (
        status in ("MOVING", "IN_MOTION", "UNDERWAY")
        or status.startswith("MOVING_TO_DOCK_")
    ):
        route = f"von {last_dock} " if last_dock else ""
        destination = str(next_dock or "unbekannt")
        message = (
            f"Unterwegs {route}nach {destination}. "
            f"Voraussichtliche Ankunft in {destination} {eta_text}."
        )
    else:
        message = f"Fährstatus derzeit nicht verfügbar ({status.lower()})."

    return {
        **ferry,
        "message": message,
        "eta_minutes": minutes,
    }


class FerryDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict]]):
    """Fetch both ferries in one API request and coordinate their data."""

    def __init__(self, hass: HomeAssistant) -> None:
        self.session = async_get_clientsession(hass)
        super().__init__(
            hass,
            logger=_LOGGER,
            name="Fähr-Radar Linz",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, dict]:
        """Fetch and prepare the data for each configured ferry."""
        try:
            async with self.session.get(
                API_URL, timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                response.raise_for_status()
                payload = await response.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as err:
            raise UpdateFailed(f"Fehler beim Abrufen der Fährdaten: {err}") from err

        found = _ferries_from_payload(payload)
        result = {}
        for ferry_name, config in FERRIES.items():
            ferry = found.get(ferry_name)
            if ferry is None:
                _LOGGER.warning("Fähre %s fehlt in der API-Antwort", ferry_name)
                result[ferry_name] = {
                    "ship_name": ferry_name,
                    "movement_state": "unavailable",
                    "message": "Für diese Fähre liegen derzeit keine API-Daten vor.",
                    "eta_minutes": None,
                }
            else:
                result[ferry_name] = _prepare_data(ferry)

        return result
