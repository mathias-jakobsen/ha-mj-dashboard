#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import (
    DASHBOARD_FILE_PATH,
    DASHBOARD_URL,
    RESOURCES_PATH,
    RESOURCES_STATIC_PATH,
    THEMES_FILE_PATH_DESTINATION,
    THEMES_FILE_PATH_SOURCE
)
from .config import MJ_Config
from .logger import LOGGER
from homeassistant.components.frontend import (
    add_extra_js_url,
    async_remove_panel,
    DOMAIN as DOMAIN_FRONTEND,
    EVENT_PANELS_UPDATED,
    SERVICE_RELOAD_THEMES
)
from homeassistant.components.lovelace import _register_panel
from homeassistant.components.lovelace.dashboard import LovelaceYAML
from homeassistant.components.lovelace.resources import ResourceStorageCollection
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader
import os
import shutil


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_initialized: bool = False


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the frontend component. """
    global _initialized
    await async_setup_resources(hass, config)
    await async_setup_themefiles(hass, config)
    setup_dashboard(hass, config)
    _initialized = True

async def async_reload(hass: HomeAssistant, old_config: MJ_Config, new_config: MJ_Config) -> None:
    """ Reloads the frontend component. """
    await async_remove(hass, old_config)
    await async_setup(hass, new_config)

async def async_remove(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Removes the frontend component. """
    remove_dashboard(hass)
    await async_remove_themefiles(hass, config)
    await async_remove_resources(hass, config)


#-----------------------------------------------------------#
#       Dashboard
#-----------------------------------------------------------#

def setup_dashboard(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the dashboard. """
    LOGGER.debug(f"Setting up the dashboard (url={DASHBOARD_URL}).")

    dashboard_config = {
        "mode": "yaml",
        "icon": config.sidepanel_icon,
        "title": config.sidepanel_title,
        "filename": DASHBOARD_FILE_PATH,
        "show_in_sidebar": True,
        "require_admin": False
    }

    hass.data["lovelace"]["dashboards"][DASHBOARD_URL] = LovelaceYAML(hass, DASHBOARD_URL, dashboard_config)
    _register_panel(hass, DASHBOARD_URL, "yaml", dashboard_config, False)

def remove_dashboard(hass: HomeAssistant) -> None:
    """ Removes the dashboard. """
    LOGGER.debug(f"Removing dashboard (url={DASHBOARD_URL}).")
    async_remove_panel(hass, DASHBOARD_URL)
    hass.data["lovelace"]["dashboards"].pop(DASHBOARD_URL, None)


#-----------------------------------------------------------#
#       Resources
#-----------------------------------------------------------#

async def async_setup_resources(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the frontend resources. """
    global _initialized

    if not config.install_custom_cards:
        return

    resources: ResourceStorageCollection = hass.data["lovelace"]["resources"]
    resources_path = hass.config.path(RESOURCES_PATH)

    if not _initialized:
        LOGGER.debug(f"Setting up static path {RESOURCES_STATIC_PATH}.")
        hass.http.register_static_path(RESOURCES_STATIC_PATH, resources_path, True)

    for filename in loader._find_files(resources_path, "*.js"):
        resource_url = filename.replace(resources_path, RESOURCES_STATIC_PATH)
        skip = False

        for item in resources.async_items():
            url: str = item["url"]

            if url.startswith(resource_url):
                skip = True
                break

        if skip:
            continue

        LOGGER.debug(f"Adding resource {resource_url.replace(RESOURCES_STATIC_PATH, '')}.")

        if isinstance(resources, ResourceStorageCollection):
            await resources.async_create_item({"res_type": "module", "url": resource_url})
        else:
            add_extra_js_url(hass, resource_url)

async def async_remove_resources(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Removes the frontend resources. """
    if not config.install_custom_cards:
        return

    resources: ResourceStorageCollection = hass.data["lovelace"]["resources"]

    if not isinstance(resources, ResourceStorageCollection):
        LOGGER.warning(f"Cannot remove resources: Lovelace mode is set to YAML. Restart Homeassistant to remove the resources.")
        return

    for item in resources.async_items():
        url: str = item["url"]

        if not url.startswith(RESOURCES_STATIC_PATH):
            continue

        LOGGER.debug(f"Removing {url.replace(RESOURCES_STATIC_PATH, '')} from the resource collection.")
        await resources.async_delete_item(item["id"])


#-----------------------------------------------------------#
#       Themes
#-----------------------------------------------------------#

async def async_setup_themefiles(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the theme files in the configured path. """
    destination_path = hass.config.path(config.themes_path, THEMES_FILE_PATH_DESTINATION)
    source_path = hass.config.path(THEMES_FILE_PATH_SOURCE)

    LOGGER.debug(f"Creating theme files at {destination_path}.")
    os.makedirs(destination_path, exist_ok=True)

    for filename in os.listdir(source_path):
        shutil.copy(source_path + filename, destination_path + filename)
    await hass.services.async_call(DOMAIN_FRONTEND, SERVICE_RELOAD_THEMES)

async def async_remove_themefiles(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Removes the theme files. """
    destination_path = hass.config.path(config.themes_path, THEMES_FILE_PATH_DESTINATION)

    if not os.path.exists(destination_path):
        return

    LOGGER.debug(f"Removing theme file at {destination_path}.")
    shutil.rmtree(destination_path)
    await hass.services.async_call(DOMAIN_FRONTEND, SERVICE_RELOAD_THEMES)