#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import MJ_UserConfig, DomainConfig
from dataclasses import dataclass
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
#       DomainRegistryEntry
#-----------------------------------------------------------#

@dataclass
class DomainRegistryEntry:
    """ A class representing a domain entry. """
    icon: str
    id: str
    priority: int


#-----------------------------------------------------------#
#       DomainRegistry
#-----------------------------------------------------------#

class DomainRegistry:
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

    def _get_domains(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, DomainRegistryEntry]:
        """ Gets a dictionary containing the domain entries. """
        result: dict[str, DomainRegistryEntry] = {}

        for domain in set([state.entity_id.split(".")[0] for state in hass.states.async_all()]):
            if domain in config.exclude.domains:
                continue

            domain_config = config.domains.get(domain, DomainConfig())
            new_entry = DomainRegistryEntry(
                icon=domain_config.icon or DEFAULT_DOMAIN_ICONS.get(domain, DEFAULT_DOMAIN_ICON),
                id=domain,
                priority=domain_config.priority
            )

            result[new_entry.id] = new_entry

        return dict(sorted(result.items(), key=lambda x: (-x[1].priority, x[1].id)))


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> DomainRegistryEntry | None:
        """ Gets a domain by id. """
        return self._domains.get(id, None)

    def update(self, config: MJ_UserConfig = None) -> None:
        """ Updates the registry. """
        if config:
            self._config = config

        self._domains = self._get_domains(self._hass, self._config)