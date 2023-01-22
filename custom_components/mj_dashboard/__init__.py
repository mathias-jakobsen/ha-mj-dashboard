#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import PLATFORMS
from .utils.logger import LOGGER
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from typing import Any


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry):
    """Called when the integration is being setup."""
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Called when a config entry is being set up."""
    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Called when a config entry is updated."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Called when a config entry has been unloaded."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Called when a config entry has been removed."""
    LOGGER.debug("Integration has been removed. Restart Homeassistant to finalize the removal.")
