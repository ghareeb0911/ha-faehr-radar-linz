"""Sensor platform for Fähr-Radar Linz."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up the ferry status sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([FerrySpeechSensor(coordinator)])


class FerrySpeechSensor(CoordinatorEntity, SensorEntity):
    """Human-readable ferry status for voice assistants."""

    _attr_has_entity_name = True
    _attr_name = "Sprachstatus"
    _attr_icon = "mdi:ferry"

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = "st_johannes_sprachstatus"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, "st_johannes")},
            name="Fähre St. Johannes",
            manufacturer="Fähr-Radar Linz",
            configuration_url="https://faehr-radar-linz.de/",
        )

    @property
    def native_value(self) -> str:
        """Return the spoken status."""
        return self.coordinator.data["message"]

    @property
    def extra_state_attributes(self) -> dict:
        """Expose useful details for automations."""
        return {
            key: value
            for key, value in self.coordinator.data.items()
            if key != "message" and value is not None
        }
