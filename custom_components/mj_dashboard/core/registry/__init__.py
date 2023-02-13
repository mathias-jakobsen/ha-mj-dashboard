#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DASHBOARD_URL, DOMAIN, PARSER_KEY_GLOBAL, TRANSLATIONS_PATH
from ..config import MJ_Config
from ..logger import LOGGER
from ..user_config import MJ_UserConfig
from .areas import AreaRegistry
from .domains import DomainRegistry
from .entities import EntityRegistry
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader
import os


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_registry: dict = None


#-----------------------------------------------------------#
#       Public Methods
#-----------------------------------------------------------#

def get_registry(hass: HomeAssistant, config: MJ_Config, reload: bool = False) -> dict:
    """ Gets the registry. """
    global _registry

    if _registry is None or reload:
        _registry = _get_registry(hass, config)

    return _registry


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _get_registry(hass: HomeAssistant, config: MJ_Config) -> dict:
    """ Gets the registry. """
    user_config_path = hass.config.path(config.user_config_path, "config/")
    user_config = _load_user_config(user_config_path)

    area_registry = AreaRegistry(hass, user_config)
    domain_registry = DomainRegistry(hass, user_config)
    entity_registry = EntityRegistry(hass, area_registry, user_config)

    button_card_templates_path = hass.config.path(f"custom_components/{DOMAIN}/lovelace/templates/button_card")
    button_card_templates = _load_button_card_templates(button_card_templates_path)

    translations_path = hass.config.path(TRANSLATIONS_PATH, f"{config.language}.yaml")
    translations = _load_translations(translations_path)

    custom_button_card_template_path = hass.config.path(config.user_config_path, "custom_templates/")
    custom_views_path = hass.config.path(config.user_config_path, "custom_views/")

    return {
        PARSER_KEY_GLOBAL: {
            "areas": area_registry,
            "button_card_templates": button_card_templates,
            "dashboard_url": DASHBOARD_URL,
            "domains": domain_registry,
            "entities": entity_registry,
            "paths": {
                "custom_button_card_templates": custom_button_card_template_path if os.path.exists(custom_button_card_template_path) else None,
                "custom_views": custom_views_path if os.path.exists(custom_views_path) else None
            },
            "translations": translations,
            "user_config": user_config
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