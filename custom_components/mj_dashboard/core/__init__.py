#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN
from .config import MJ_Config
from .frontend import *
from .logger import LOGGER
from .registry import *
from .yaml_loader import *
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant


#-----------------------------------------------------------#
#       MJ Dashboard
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Sets up the required components. """
    if DOMAIN in hass.data:
        return await async_reload(hass, config_entry)

    config = hass.data[DOMAIN] = MJ_Config(**{**config_entry.data, **config_entry.options})
    await frontend.async_setup(hass, config)
    await registry.async_setup(hass, config)
    yaml_loader.setup(hass, config)

async def async_reload(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """ Reloads the components. """
    if DOMAIN not in hass.data:
        return await async_setup(hass, config_entry)

    old_config = hass.data[DOMAIN]
    new_config = hass.data[DOMAIN] = MJ_Config(**{**config_entry.data, **config_entry.options})

    await frontend.async_reload(hass, old_config, new_config)
    await registry.async_reload(hass, new_config)
    yaml_loader.reload(hass, new_config)

async def async_remove(hass: HomeAssistant) -> None:
    """ Removes the components. """
    if DOMAIN not in hass.data:
        return

    await frontend.async_remove(hass, hass.data[DOMAIN])
    await registry.async_remove(hass)
    yaml_loader.remove()
    hass.data.pop(DOMAIN)