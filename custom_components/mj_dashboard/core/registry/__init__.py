#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DASHBOARD_URL, DOMAIN, MEDIA_QUERY_MOBILE, PARSER_KEY_GLOBAL, TRANSLATIONS_PATH
from ..config import MJ_Config
from ..logger import LOGGER
from ..user_config import MJ_UserConfig
from .areas import AreaRegistry
from .domains import DomainRegistry
from .entities import EntityRegistry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.entity_registry import EVENT_DEVICE_REGISTRY_UPDATED, EVENT_ENTITY_REGISTRY_UPDATED
from homeassistant.helpers.event import async_call_later
from homeassistant.util.yaml import loader
from typing import Any, Callable
import os, stat


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

UPDATE_INTERVAL = 3.5


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_registry: dict = None
_registry_remove_listeners: list[Callable] = []
_registry_update_remove_listeners: list[Callable] = []
_timer_remove_listener: Callable = None
_user_config: dict = None
_user_config_modification_times: dict[str, int] = {}


#-----------------------------------------------------------#
#       Public Variables
#-----------------------------------------------------------#

area_registry: AreaRegistry = None
domain_registry: DomainRegistry = None
entity_registry: EntityRegistry = None


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

async def async_setup(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the registry and its listeners. """
    global area_registry, domain_registry, entity_registry, _registry_remove_listeners, _user_config

    user_config_path = hass.config.path(config.user_config_path, "config/")
    _user_config = _load_user_config(user_config_path)

    area_registry = AreaRegistry(hass, _user_config)
    domain_registry = DomainRegistry(hass, _user_config)
    entity_registry = EntityRegistry(hass, area_registry, _user_config)

    _registry_remove_listeners.append(hass.bus.async_listen(EVENT_AREA_REGISTRY_UPDATED, lambda *args: _update(hass, _user_config)))
    _registry_remove_listeners.append(hass.bus.async_listen(EVENT_DEVICE_REGISTRY_UPDATED, lambda *args: _update(hass, _user_config)))
    _registry_remove_listeners.append(hass.bus.async_listen(EVENT_ENTITY_REGISTRY_UPDATED, lambda *args: _update(hass, _user_config)))

async def async_reload(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Reloads the registry. """
    await async_remove()
    await async_setup(hass, config)

async def async_remove() -> None:
    """ Removes the registry event listeners. """
    while _registry_remove_listeners:
        _registry_remove_listeners.pop()()


#-----------------------------------------------------------#
#       Public Methods
#-----------------------------------------------------------#

def get_registry(hass: HomeAssistant, config: MJ_Config) -> dict:
    """ Gets the registry. """
    global _registry, _timer_remove_listener

    if _registry is None or _timer_remove_listener is None:
        _timer_remove_listener = async_call_later(hass, UPDATE_INTERVAL, _async_on_timer_expired)
        _registry = _get_registry(hass, config)

    return _registry


#-----------------------------------------------------------#
#       Private Event Handlers
#-----------------------------------------------------------#

async def _async_on_timer_expired(*args: Any) -> None:
    """ Triggered when the update timer has expired. """
    global _timer_remove_listener
    _timer_remove_listener = None


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _check_user_config_modifications(hass: HomeAssistant, path: str) -> bool:
    """ Checks whether the user configuration has been modified. """
    result = False

    for current_directory, directories, files in os.walk(path):
        for file in files:
            file = hass.config.path(current_directory, file)
            file_mtime = os.stat(file)[stat.ST_MTIME]

            if file not in _user_config_modification_times:
                result = True
            elif _user_config_modification_times[file] != file_mtime:
                result = True

            _user_config_modification_times[file] = file_mtime

        for directory in directories:
            directory = hass.config.path(current_directory, directory)
            directory_mtime = os.stat(directory)[stat.ST_MTIME]

            if directory not in _user_config_modification_times:
                result = True
            elif _user_config_modification_times[directory] != directory_mtime:
                result = True

            _user_config_modification_times[directory] = directory_mtime

    return result

def _get_registry(hass: HomeAssistant, config: MJ_Config) -> dict:
    """ Gets the registry. """
    global area_registry, domain_registry, entity_registry, _user_config

    user_config_path = hass.config.path(config.user_config_path, "config/")
    user_config_modified = _check_user_config_modifications(hass, user_config_path)

    if user_config_modified:
        _user_config = _load_user_config(user_config_path)
        _update(hass, _user_config)

    button_card_templates = _load_button_card_templates(hass.config.path(f"custom_components/{DOMAIN}/lovelace/templates/button_card"))
    translations = _load_translations(hass.config.path(TRANSLATIONS_PATH, f"{config.language}.yaml"))

    custom_button_card_template_path = hass.config.path(config.user_config_path, "custom_templates/")
    custom_views_path = hass.config.path(config.user_config_path, "custom_views/")

    return {
        PARSER_KEY_GLOBAL: {
            "areas": area_registry,
            "button_card_templates": button_card_templates,
            "dashboard_url": DASHBOARD_URL,
            "domains": domain_registry,
            "entities": entity_registry,
            "media_query": {
                "mobile": MEDIA_QUERY_MOBILE
            },
            "paths": {
                "custom_button_card_templates": custom_button_card_template_path if os.path.exists(custom_button_card_template_path) else None,
                "custom_views": custom_views_path if os.path.exists(custom_views_path) else None
            },
            "translations": translations,
            "user_config": _user_config
        }
    }

def _load_button_card_templates(path: str) -> list[str]:
    """ Loads a list of available button card templates. """
    result = []

    for filename in loader._find_files(path, "*.yaml"):
        if filename.endswith("__custom__.yaml"):
            continue

        templates = loader.load_yaml(filename).keys()
        result.extend(templates)

    return result

def _load_translations(path: str) -> dict[str, str]:
    """ Loads the translation strings. """
    if os.path.exists(path):
        return loader.load_yaml(path)

    return {}

def _load_user_config(path: str) -> MJ_UserConfig:
    """ Loads the user configuration from the configuration directory. """
    result = {}

    if os.path.exists(path):
        for filename in loader._find_files(path, "*.yaml"):
            config = loader.load_yaml(filename)

            if isinstance(config, dict):
                result.update(config)

        result = MJ_UserConfig.get_schema()(result)
        LOGGER.debug(f"User configuration loaded from {path}.")
    else:
        LOGGER.warning(f"Unable to load user configuration: Path {path} does not exist.")

    return MJ_UserConfig(result)

def _update(hass: HomeAssistant, config: MJ_UserConfig = None) -> None:
    """ Updates the registry. """
    global area_registry, domain_registry, entity_registry

    area_registry.update(config)
    domain_registry.update(config)
    entity_registry.update(config)

    for listener in _registry_update_remove_listeners:
        hass.async_create_task(listener())