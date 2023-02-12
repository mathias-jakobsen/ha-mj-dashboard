#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DOMAIN
from ..logger import LOGGER
from .area_config import AreaLocationsConfig, AreaConfig
from .domain_config import DomainConfig
from .exclude_config import ExcludeConfig
import voluptuous as vol


#-----------------------------------------------------------#
#       MJ_UserConfig
#-----------------------------------------------------------#

class MJ_UserConfig:
    """ A class representing the user configuration. """

    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @staticmethod
    def get_schema() -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("areas", default={}): {str: {
                vol.Optional("entities"): { str: str },
                vol.Optional("icon"): str,
                vol.Optional("location"): str,
                vol.Optional("priority"): int
            }},
            vol.Required("area_locations", default={}): {
                vol.Optional("icon"): str,
                vol.Optional("priority"): int
            },
            vol.Required("domains", default={}): {
                str: {
                    vol.Optional("icon"): str,
                    vol.Required("priority", default=1): int
                }
            },
            vol.Required("exclude", default={}): {
                vol.Required("areas", default=[]): [str],
                vol.Required("domains", default=[]): [str],
                vol.Required("entities", default=[]): [str]
            },
            vol.Required("scene_colors", default={}): {str: str},
            vol.Required("weather", default={}): {
                vol.Required("entities", default={}): {str: str}
            }

        }, extra=True)


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: dict[str, AreaConfig]
    area_locations: dict[str, AreaLocationsConfig]
    domains: dict[str, DomainConfig]
    exclude: ExcludeConfig


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config: dict):
        self.areas = { key: AreaConfig(**value) for key, value in config.pop("areas", {}).items() }
        self.area_locations = { key: AreaLocationsConfig(**value) for key, value in config.pop("area_locations", {}).items() }
        self.domains = { key: DomainConfig(**value) for key, value in config.pop("domains", {}).items() }
        self.exclude = ExcludeConfig(**config.pop("exclude", {}))

        for key, value in config.items():
            setattr(self, key, value)


