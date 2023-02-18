#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..config import MJ_Config
from dataclasses import dataclass, fields
from homeassistant.core import HomeAssistant
import os


#-----------------------------------------------------------#
#       MJ_Paths
#-----------------------------------------------------------#

@dataclass
class MJ_UserConfigPaths:
    """ A class representing the relevant paths. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    button_card_templates: str
    config: str
    views: str
    yaml_templates: str


    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @classmethod
    def from_config(cls, hass: HomeAssistant, config: MJ_Config, create_paths: bool = True):
        """ Creates an instance from a configuration. """

        paths = MJ_UserConfigPaths(
                config=hass.config.path(config.user_config_path, "config/"),
                button_card_templates=hass.config.path(config.user_config_path, "templates/button_card/"),
                views=hass.config.path(config.user_config_path, "views/"),
                yaml_templates=hass.config.path(config.user_config_path, "templates/yaml/")
        )

        if create_paths:
            paths.create_paths()

        return paths


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def create_paths(self) -> None:
        """ Creates the paths if they do not exist. """
        for field in fields(self):
            path = getattr(self, field.name)

            if not os.path.exists(path):
                os.makedirs(path)