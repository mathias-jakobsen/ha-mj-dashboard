#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from ...const import DASHBOARD_URL, DOMAIN, TRANSLATIONS_PATH
from ..config import MJ_Config
from ..logger import LOGGER
from ..user_config import MJ_UserConfig
from .areas import MJ_AreaRegistry
from .domains import MJ_DomainRegistry
from .entities import MJ_EntityRegistry
from .user_config_paths import MJ_UserConfigPaths
from dataclasses import dataclass
from homeassistant.core import HomeAssistant
from homeassistant.util.yaml import loader
import os


#-----------------------------------------------------------#
#       MJ_Registry
#-----------------------------------------------------------#

@dataclass
class MJ_Registry:
    areas: MJ_AreaRegistry
    button_card_templates: list[str]
    dashboard_url: str
    domains: MJ_DomainRegistry
    entities: MJ_EntityRegistry
    translations: dict[str, str]
    user_config: MJ_UserConfig
    user_config_paths: MJ_UserConfigPaths

    @classmethod
    def from_config(cls, hass: HomeAssistant, config: MJ_Config):
        """ Creates an instance from a configuration. """
        translations_path = hass.config.path(TRANSLATIONS_PATH, f"{config.language}.yaml")
        user_config_paths = MJ_UserConfigPaths.from_config(hass, config)
        user_config = cls.load_user_config(user_config_paths.config)

        areas = MJ_AreaRegistry(hass, user_config)
        domains = MJ_DomainRegistry(hass, user_config)
        entities = MJ_EntityRegistry(hass, areas, user_config)

        return MJ_Registry(
            areas=areas,
            button_card_templates=cls.load_button_card_templates(hass.config.path(f"custom_components/{DOMAIN}/lovelace/templates/button_card")),
            dashboard_url=DASHBOARD_URL,
            domains=domains,
            entities=entities,
            translations=cls.load_translations(translations_path),
            user_config=user_config,
            user_config_paths=user_config_paths
        )

    @staticmethod
    def load_button_card_templates(path: str) -> list[str]:
        """ Loads a list of available button card templates. """
        result = []

        if os.path.exists(path):
            for filename in loader._find_files(path, "*.yaml"):
                if filename.endswith("__custom__.yaml"):
                    continue

                templates = loader.load_yaml(filename, parse_jinja=False).keys()
                result.extend(templates)
        else:
            LOGGER.warning(f"Unable to load button card templates list: Path {path} does not exist.")

        return result

    @staticmethod
    def load_translations(path: str) -> dict[str, str]:
        """ Loads the translation strings. """
        if os.path.exists(path):
            return loader.load_yaml(path)
        else:
            LOGGER.warning(f"Unable to load translations: Path {path} does not exist.")

        return {}

    @staticmethod
    def load_user_config(path: MJ_Config) -> MJ_UserConfig:
        """ Loads the user configuration from the configuration directory. """
        result = {}

        if os.path.exists(path):
            for filename in loader._find_files(path, "*.yaml"):
                config = loader.load_yaml(filename)

                if isinstance(config, dict):
                    result.update(config)

            LOGGER.debug(f"User configuration loaded from {path}.")
        else:
            LOGGER.warning(f"Unable to load user configuration: Path {path} does not exist.")

        return MJ_UserConfig.from_config(result)

