#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..logger import LOGGER
from ..user_config import MJ_UserConfig
from dataclasses import dataclass, field, KW_ONLY
from homeassistant.core import HomeAssistant
from homeassistant.helpers.area_registry import async_get as async_get_areas


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

DEFAULT_AREA_ICON = "mdi:texture-box"
DEFAULT_AREA_ICONS = {
    "mdi:baby": ["Child's Room", "Børneværelse"],
    "mdi:bed": ["Guest Room", "Gæsteværelse"],
    "mdi:bed-king": ["Bedroom", "Soveværelse"],
    "mdi:bike": ["Bike Room", "Cykelrum"],
    "mdi:chair-rolling": ["Office", "Kontor"],
    "mdi:coat-rack": ["Entrance", "Hallway", "Gang", "Entré", "Entre"],
    "mdi:garage": ["Garage"],
    "mdi:hammer-wrench": ["Tool Shed", "Værksted"],
    "mdi:pot-steam": ["Kitchen", "Køkken"],
    "mdi:silverware-fork-knife": ["Dining Room", "Kitchen-Dining Room", "Spisestue", "Køkkenalrum"],
    "mdi:sofa": ["Living Room", "Stue"],
    "mdi:toilet": ["Bathroom", "Badeværelse", "Gæstetoilet"],
    "mdi:treasure-chest": ["Storage Room"],
    "mdi:washing-machine": ["Utility Room", "Bryggers"],
    "mdi:wardrobe": ["Walk In", "Wardrobe", "Garderobe"]
}


#-----------------------------------------------------------#
#       MJ_AreaRegistryEntry
#-----------------------------------------------------------#

@dataclass(kw_only=True)
class MJ_AreaRegistryEntry:
    """ A class representing an area entry. """
    id: str
    name: str
    _: KW_ONLY
    color: str | None = None
    domain_favorites: list[str] | None = None
    entity_groups: dict[str, list[str]] | None = None
    icon: str | None = None
    location: str | None = None
    priority: int = 1


#-----------------------------------------------------------#
#       MJ_AreaRegistry
#-----------------------------------------------------------#

class MJ_AreaRegistry:
    """ A class representing an area registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MJ_UserConfig):
        self._areas: dict[str, MJ_AreaRegistryEntry] = self._get_areas(hass, config)
        self._config: MJ_UserConfig = config
        self._hass: HomeAssistant = hass


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for entry in self._areas.values():
            yield entry


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_areas(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, MJ_AreaRegistryEntry]:
        """ Gets a dictionary containing the area entries. """
        area_registry = async_get_areas(hass).areas
        result: dict[str, MJ_AreaRegistryEntry] = {}

        for area in area_registry.values():
            if area.id in config.areas.exclude or area.name in config.areas.exclude:
                continue

            area_config = config.areas.customize_global | config.areas.customize.get(area.id, config.areas.customize.get(area.name, {}))
            new_entry = MJ_AreaRegistryEntry(
                id=area.id,
                name=area.name,
                **area_config
            )

            if new_entry.icon is None:
                new_entry.icon = self._get_area_icon(new_entry)

            result[new_entry.id] = new_entry

        return dict(sorted(result.items(), key=lambda x: (-x[1].priority, x[1].name)))

    def _get_area_icon(self, area: MJ_AreaRegistryEntry) -> str:
        """ Gets the icon for an area. """
        icon_match = next(filter(lambda x: area.id in x[1] or area.name in x[1], DEFAULT_AREA_ICONS.items()), None)

        if icon_match:
            return icon_match[0]

        return DEFAULT_AREA_ICON


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def areas(self) -> dict[str, MJ_AreaRegistryEntry]:
        """ Gets the areas. """
        return self._areas

    @property
    def card_size(self) -> str:
        """ Gets the card size. """
        return self._config.areas.card_size


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> MJ_AreaRegistryEntry | None:
        """ Gets an area by id. """
        return self._areas.get(id, None)

    def get_by_name(self, name: str) -> MJ_AreaRegistryEntry | None:
        """ Gets an area by name. """
        return next((area for area in self._areas.values() if area.name == name), None)

    def group_by_location(self) -> list[tuple[str, list[MJ_AreaRegistryEntry]]]:
        """ Gets a list of areas grouped by location. """
        result: dict[str, list[MJ_AreaRegistryEntry]] = { location: [] for location in self._config.areas.locations }
        result_others: list[MJ_AreaRegistryEntry] = []

        for area in self._areas.values():
            location = area.location

            if location is None:
                result_others.append(area)
                continue

            if not location in result:
                result[location] = []

            result[location].append(area)

        result["__others__"] = result_others
        return result.items()

    def update(self, config: MJ_UserConfig = None) -> None:
        """ Updates the registry. """
        if config:
            self._config = config

        self._areas = self._get_areas(self._hass, self._config)