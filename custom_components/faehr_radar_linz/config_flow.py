"""Config flow for Fähr-Radar Linz."""

from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN


class FaehrRadarLinzConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Fähr-Radar Linz."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Add the integration without requiring credentials."""
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Fähr-Radar Linz", data={})

        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return the options flow."""
        return FaehrRadarLinzOptionsFlow()


class FaehrRadarLinzOptionsFlow(config_entries.OptionsFlow):
    """Handle options for the integration."""

    async def async_step_init(self, user_input=None):
        """No options are currently available."""
        return self.async_create_entry(title="", data={})
