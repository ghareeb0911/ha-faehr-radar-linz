"""Sensor platform for Fähr-Radar Linz."""

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, FERRIES


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
) -> None:
    """Set up one status sensor for each ferry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            FerrySpeechSensor(coordinator, ferry_name, config)
            for ferry_name, config in FERRIES.items()
        ]
    )


class FerrySpeechSensor(CoordinatorEntity, SensorEntity):
    """Human-readable ferry status with original API attributes."""

    _attr_has_entity_name = True
    _attr_name = "Status"
    _attr_icon = "mdi:ferry"

    def __init__(self, coordinator, ferry_name: str, config: dict) -> None:
        """Initialize the sensor for one ferry."""
        super().__init__(coordinator)
        self.ferry_name = ferry_name
        self._attr_unique_id = f"{config['device_id']}_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, config["device_id"])},
            name=config["device_name"],
            manufacturer="Fähr-Radar Linz",
            configuration_url="https://github.com/ghareeb0911/ha-faehr-radar-linz",
        )

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
