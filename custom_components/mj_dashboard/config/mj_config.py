#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DOMAIN, NAME
from dataclasses import dataclass, field
from homeassistant.helpers.selector import (
    BooleanSelector, BooleanSelectorConfig,
    IconSelector, IconSelectorConfig,
    SelectSelector, SelectSelectorConfig, SelectSelectorMode,
    TextSelector, TextSelectorConfig
)
from typing import ClassVar
import voluptuous as vol


#-----------------------------------------------------------#
#       MatjakConfig
#-----------------------------------------------------------#

@dataclass
class MJ_Config:
    """ A class representing the ConfigFlow options. """

    #--------------------------------------------#
    #       Constants
    #--------------------------------------------#

    LANGUAGES: ClassVar[list[str]] = ["en", "dk"]


    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    language: str = field(default=LANGUAGES[0])
    sidepanel_icon: str = "mdi:view-dashboard"
    sidepanel_title: str = NAME
    themes_path: str = "themes/"
    user_config_path: str = f"{DOMAIN}/"
    install_custom_cards: bool = True


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    def get_schema(self) -> vol.Schema:
        """ Gets the voluptuous schema. """
        return vol.Schema({
            vol.Required("sidepanel_title", default=self.sidepanel_title): TextSelector(TextSelectorConfig()),
            vol.Required("sidepanel_icon", default=self.sidepanel_icon): IconSelector(IconSelectorConfig(placeholder=self.sidepanel_icon)),
            vol.Required("language", default=self.language): SelectSelector(SelectSelectorConfig(mode=SelectSelectorMode.DROPDOWN)),
            vol.Required("themes_path", default=self.themes_path): TextSelector(TextSelectorConfig()),
            vol.Required("user_config_path", default=self.user_config_path): TextSelector(TextSelectorConfig()),
            vol.Required("install_custom_cards", default=self.install_custom_cards): BooleanSelector(BooleanSelectorConfig())
        })
