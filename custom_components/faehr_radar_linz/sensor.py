"""Sensor platform for Fährinformation Linz/Kripp."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfLength, UnitOfSpeed
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FERRIES


FERRY_SENSORS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(key="ship_name", name="Schiffsname", icon="mdi:ferry"),
    SensorEntityDescription(key="movement_state", name="Bewegungsstatus", icon="mdi:ship-wheel"),
    SensorEntityDescription(key="status", name="API-Status", icon="mdi:information-outline"),
    SensorEntityDescription(key="stationary_location", name="Standort", icon="mdi:map-marker"),
    SensorEntityDescription(key="last_dock", name="Letzter Anleger", icon="mdi:anchor"),
    SensorEntityDescription(key="next_dock", name="Nächster Anleger", icon="mdi:map-marker-radius"),
    SensorEntityDescription(key="eta_dock_a_name", name="Anleger A", icon="mdi:map-marker"),
    SensorEntityDescription(key="eta_dock_b_name", name="Anleger B", icon="mdi:map-marker"),
    SensorEntityDescription(key="eta_dock_a", name="ETA Anleger A", icon="mdi:clock-outline"),
    SensorEntityDescription(key="eta_dock_b", name="ETA Anleger B", icon="mdi:clock-outline"),
    SensorEntityDescription(key="eta_minutes", name="ETA Minuten", icon="mdi:timer-sand", native_unit_of_measurement="min"),
    SensorEntityDescription(
        key="speed_knots", name="Geschwindigkeit Knoten", icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfSpeed.KNOTS, device_class=SensorDeviceClass.SPEED,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="speed_kmh", name="Geschwindigkeit km/h", icon="mdi:speedometer",
        native_unit_of_measurement=UnitOfSpeed.KILOMETERS_PER_HOUR,
        device_class=SensorDeviceClass.SPEED, suggested_display_precision=2,
    ),
    SensorEntityDescription(key="course_degrees", name="Kurs", icon="mdi:compass", native_unit_of_measurement="°"),
    SensorEntityDescription(
        key="dock_distance_meters", name="Entfernung zum Anleger", icon="mdi:map-marker-distance",
        native_unit_of_measurement=UnitOfLength.METERS, device_class=SensorDeviceClass.DISTANCE,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(key="progress_percent", name="Fortschritt", icon="mdi:progress-clock", native_unit_of_measurement=PERCENTAGE),
    SensorEntityDescription(key="timestamp_formatted", name="Zeitstempel", icon="mdi:clock-digital"),
    SensorEntityDescription(key="timestamp", name="Zeitstempel Unix", icon="mdi:clock"),
    SensorEntityDescription(key="mmsi", name="MMSI", icon="mdi:identifier"),
    SensorEntityDescription(key="latitude", name="Breitengrad", icon="mdi:latitude"),
    SensorEntityDescription(key="longitude", name="Längengrad", icon="mdi:longitude"),
    SensorEntityDescription(key="at_dock_a", name="Am Anleger A", icon="mdi:anchor"),
    SensorEntityDescription(key="at_dock_b", name="Am Anleger B", icon="mdi:anchor"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the status and data sensors for each ferry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities = []
    for ferry_name, config in FERRIES.items():
        entities.append(FerrySpeechSensor(coordinator, ferry_name, config))
        entities.extend(
            FerryDataSensor(coordinator, ferry_name, config, description)
            for description in FERRY_SENSORS
        )
    async_add_entities(entities)


class FerrySpeechSensor(CoordinatorEntity, SensorEntity):
    """Human-readable ferry status with original API attributes."""

    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_icon = "mdi:ferry"

    def __init__(self, coordinator, ferry_name: str, config: dict) -> None:
        """Initialize the status sensor for one ferry."""
        super().__init__(coordinator)
        self.ferry_name = ferry_name
        self._attr_unique_id = f"{config['device_id']}_status"
        self._attr_device_info = _device_info(config)

    @property
    def native_value(self) -> str:
        """Return the spoken status."""
        return self.coordinator.data[self.ferry_name]["message"]

    @property
    def extra_state_attributes(self) -> dict:
        """Expose all original API fields plus calculated values."""
        return {
            key: value
            for key, value in self.coordinator.data[self.ferry_name].items()
            if key != "message"
        }


class FerryDataSensor(CoordinatorEntity, SensorEntity):
    """Expose one ferry API field as an independently usable sensor."""

    entity_description: SensorEntityDescription
    _attr_has_entity_name = True

    def __init__(self, coordinator, ferry_name: str, config: dict, description: SensorEntityDescription) -> None:
        """Initialize an individual data sensor."""
        super().__init__(coordinator)
        self.ferry_name = ferry_name
        self.entity_description = description
        self._attr_unique_id = f"{config['device_id']}_{description.key}"
        self._attr_device_info = _device_info(config)

    @property
    def native_value(self):
        """Return the selected API value, converting speed when requested."""
        ferry = self.coordinator.data[self.ferry_name]
        key = self.entity_description.key

        if key == "speed_kmh":
            speed_knots = ferry.get("speed_knots")
            if speed_knots is None:
                return None
            try:
                return round(float(speed_knots) * 1.852, 2)
            except (TypeError, ValueError):
                return None

        if key in ("latitude", "longitude"):
            position = ferry.get("position") or {}
            if not isinstance(position, dict):
                return None
            return position.get("lat" if key == "latitude" else "lon")

        value = ferry.get(key)
        if isinstance(value, bool):
            return "Ja" if value else "Nein"
        return value


def _device_info(config: dict) -> DeviceInfo:
    """Return shared device information for all entities of a ferry."""
    return DeviceInfo(
        identifiers={(DOMAIN, config["device_id"])},
        name=config["device_name"],
        manufacturer="Fährinformation Linz/Kripp",
        configuration_url="https://github.com/ghareeb0911/faehrinformation-linz-kripp",
    )
