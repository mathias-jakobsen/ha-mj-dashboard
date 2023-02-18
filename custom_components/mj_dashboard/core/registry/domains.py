#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..logger import LOGGER
from ..user_config import MJ_UserConfig
from dataclasses import dataclass, KW_ONLY
from homeassistant.core import HomeAssistant


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_DOMAIN_ICON = "mdi:eye"
DEFAULT_DOMAIN_ICONS = {
    "automation": "mdi:robot",
    "binary_sensor": "mdi:checkbox-blank-circle-outline",
    "button": "mdi:gesture-tap-button",
    "camera": "mdi:cctv",
    "climate": "mdi:thermostat",
    "counter": "mdi:counter",
    "cover": "mdi:window-shutter",
    "device_tracker": "mdi:radar",
    "fan": "mdi:fan",
    "input_boolean": "mdi:toggle-switch-outline",
    "input_button": "mdi:gesture-tap-button",
    "input_number": "mdi:ray-vertex",
    "input_select": "mdi:format-list-bulleted",
    "input_text": "mdi:form-textbox",
    "light": "mdi:lightbulb",
    "lock": "mdi:lock",
    "media_player": "mdi:cast-connected",
    "number": "mdi:ray-vertex",
    "person": "mdi:account",
    "remote": "mdi:remote",
    "scene": "mdi:palette",
    "script": "mdi:script-text",
    "select": "mdi:format-list-bulleted",
    "sensor": "mdi:eye",
    "sun": "mdi:weather-sunny",
    "switch": "mdi:power-plug",
    "timer": "mdi:timer",
    "update": "mdi:update",
    "weather": "mdi:cloud",
    "zone": "mdi:map-marker-radius"
}


#-----------------------------------------------------------#
#       MJ_DomainRegistryEntry
#-----------------------------------------------------------#

@dataclass(kw_only=True)
class MJ_DomainRegistryEntry:
    """ A class representing a domain entry. """
    id: str
    _: KW_ONLY
    color: str | None = None
    icon: str | None = None


#-----------------------------------------------------------#
#       MJ_DomainRegistry
#-----------------------------------------------------------#

class MJ_DomainRegistry:
    """ A class representing a domain registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MJ_UserConfig):
        self._config: MJ_UserConfig = config
        self._domains: dict[str, DomainRegistryEntry] = self._get_domains(hass, config)
        self._hass: HomeAssistant = hass


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for entry in self._domains.values():
            yield entry


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_domains(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, MJ_DomainRegistryEntry]:
        """ Gets a dictionary containing the domain entries. """
        result: dict[str, MJ_DomainRegistryEntry] = {}

        for domain in set([state.entity_id.split(".")[0] for state in hass.states.async_all()]):
            if domain in config.domains.exclude:
                continue

            domain_config = config.domains.customize.get(domain, {})

            new_entry = MJ_DomainRegistryEntry(
                id=domain,
                **domain_config
            )

            if new_entry.color is None:
                new_entry.color = f"var(--mj-color-{domain}, var(--primary-color))"

            if new_entry.icon is None:
                new_entry.icon = DEFAULT_DOMAIN_ICONS.get(domain, DEFAULT_DOMAIN_ICON)

            result[new_entry.id] = new_entry

        return dict(sorted(result.items(), key=lambda x: (config.domains.favorites.index(x[0]) if x[0] in config.domains.favorites else -1, x[0])))


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> MJ_DomainRegistryEntry | None:
        """ Gets a domain by id. """
        LOGGER.debug(id)
        return self._domains.get(id, None)

    def update(self, config: MJ_UserConfig = None) -> None:
        """ Updates the registry. """
        if config:
            self._config = config

        self._domains = self._get_domains(self._hass, self._config)