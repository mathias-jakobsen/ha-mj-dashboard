#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from .const import PLATFORMS
from .core import async_remove as mj_dashboard_async_remove, async_setup as mj_dashboard_async_setup
from .core.logger import LOGGER
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STARTED
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
    async def async_setup(*args: Any) -> None:
        await mj_dashboard_async_setup(hass, config_entry)
        config_entry.async_on_unload(config_entry.add_update_listener(async_update_options))
        hass.async_create_task(hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS))

    if hass.is_running:
        await async_setup()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, async_setup)

    return True

async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Called when a config entry is updated."""
    await hass.config_entries.async_reload(config_entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Called when a config entry has been unloaded."""
    return all(
        [
            await hass.config_entries.async_forward_entry_unload(config_entry, platform)
            for platform in PLATFORMS
        ]
    )

async def async_remove_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Called when a config entry has been removed."""
    await mj_dashboard_async_remove(hass, config_entry)
    LOGGER.debug("Integration has been removed. Restart Homeassistant to finalize the removal.")
