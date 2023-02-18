#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DOMAIN
from ..logger import LOGGER
from .area_config import MJ_AreasUserConfig
from .domain_config import MJ_UserDomainsConfig
from .entities_config import MJ_UserEntitiesConfig
import voluptuous as vol


#-----------------------------------------------------------#
#       MJ_UserConfig
#-----------------------------------------------------------#

class MJ_UserConfig:
    """ A class representing the user configuration. """

    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @classmethod
    def from_config(cls, config: dict):
        """ Creates an instance from a configuration. """
        return MJ_UserConfig(cls.get_schema()(config))

    @staticmethod
    def get_schema() -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("areas", default={}): {
                vol.Required("customize", default={}): {str: {
                    vol.Optional("color"): str,
                    vol.Optional("domain_favorites", default=[]): [str],
                    vol.Optional("icon"): str,
                    vol.Optional("location"): str,
                    vol.Optional("priority"): int
                },
                vol.Required("customize_global", default={}): {
                    vol.Optional("domain_favorites"): str
                },
                vol.Required("exclude", default=[]): [str],
                vol.Required("locations", default=[]): [str]
            }},

            vol.Required("domains", default={}): {
                vol.Required("customize"): {str: {
                    vol.Optional("color"): str,
                    vol.Optional("icon"): str
                }},
                vol.Required("exclude", default=[]): [str],
                vol.Required("favorites", default=[]): [str]
            },

            vol.Required("entities", default={}): {
                vol.Required("customize", default={}): {
                    vol.Required("battery", default={}): {
                        vol.Required("levels", default={}): {str: {
                            vol.Required("color"): str,
                            vol.Required("value"): vol.All(int, vol.Range(min=0, max=100))
                        }}
                    }
                },
                vol.Required("exclude", default=[]): [str],
                vol.Required("favorites", default=[]): [str]
            },

            vol.Required("mediaquery", default={}): {
                vol.Required("desktop", default="(min-width: 870px)"): str,
                vol.Required("mobile", default="(max-width: 869px)"): str,
            },

            vol.Required("navbar", default={}): {
                vol.Required("buttons", default=[]): [{
                    vol.Required("icon"): str,
                    vol.Required("navigation_path"): str,
                    vol.Required("title"): str
                }],
                vol.Required("num_buttons_desktop", default=4): vol.All(int, vol.Range(min=1)),
                vol.Required("num_buttons_mobile", default=2): vol.All(int, vol.Range(min=1))
            },
            vol.Required("weather", default={}): {
                vol.Required("entities", default={}): {str: str}
            }
        }, extra=True)


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: MJ_AreasUserConfig
    domains: MJ_UserDomainsConfig
    entities: MJ_UserEntitiesConfig


    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config: dict):
        self.areas = MJ_AreasUserConfig(**config.pop("areas", {}))
        self.domains = MJ_UserDomainsConfig(**config.pop("domains", {}))
        self.entities = MJ_UserEntitiesConfig(**config.pop("entities", {}))

        for key, value in config.items():
            setattr(self, key, value)


