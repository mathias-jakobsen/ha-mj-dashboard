#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from __future__ import annotations
from .const import DOMAIN
from .core.config import MJ_Config
from .utils.logger import LOGGER
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

# ------ Abort Reasons ---------------
ABORT_REASON_ALREADY_CONFIGURED = "already_configured"


#-----------------------------------------------------------#
#       Config Flow
#-----------------------------------------------------------#

class MD_ConfigFlow(ConfigFlow, domain=DOMAIN):
    #--------------------------------------------#
    #       Static Properties
    #--------------------------------------------#

    VERSION = 1


    #--------------------------------------------#
    #       Static Methods
    #--------------------------------------------#

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> MD_OptionsFlow:
        return MD_OptionsFlow(config_entry)


    #--------------------------------------------#
    #       Methods
    #--------------------------------------------#

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        if len(self._async_current_entries()) > 0:
            return self.async_abort(reason=ABORT_REASON_ALREADY_CONFIGURED)

        if user_input is not None:
            return self.async_create_entry(title=DOMAIN, data=user_input)

        config = MJ_Config(**(user_input or {}))
        schema = config.get_schema()

        return self.async_show_form(step_id="user", data_schema=schema)


#-----------------------------------------------------------#
#       Options Flow
#-----------------------------------------------------------#

class MD_OptionsFlow(OptionsFlow):
    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, config_entry: ConfigEntry):
        self.data = { **config_entry.data, **config_entry.options }


    #--------------------------------------------#
    #       Steps - Init
    #--------------------------------------------#

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """ Called when configuring the options from the UI. """
        if user_input is not None:
            return self.async_create_entry(title=DOMAIN, data=user_input)

        config = MJ_Config(**(user_input or self.data))
        schema = config.get_schema()

        return self.async_show_form(step_id="init", data_schema=schema)