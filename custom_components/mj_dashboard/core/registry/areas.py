#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..user_config import AreaConfig, AreaLocationsConfig, MJ_UserConfig
from dataclasses import dataclass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.area_registry import async_get as async_get_areas
from typing import Optional


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
#       EntityRegistryEntry
#-----------------------------------------------------------#

@dataclass
class AreaRegistryEntry:
    """ A class representing an area entry. """
    id: str
    priority: int
    color: Optional[tuple[int, int, int]] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    name: Optional[str] = None


#-----------------------------------------------------------#
#       AreaRegistry
#-----------------------------------------------------------#

class AreaRegistry:
    """ A class representing an area registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, config: MJ_UserConfig):
        self._areas: dict[str, AreaRegistryEntry] = self._get_areas(hass, config)
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

    def _get_areas(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, AreaRegistryEntry]:
        """ Gets a dictionary containing the area entries. """
        area_registry = async_get_areas(hass).areas
        result: dict[str, AreaRegistryEntry] = {}

        for area in area_registry.values():
            if area.id in config.exclude.areas or area.name in config.exclude.areas:
                continue

            area_config = config.areas.get(area.id, config.areas.get(area.name, AreaConfig()))
            new_entry = AreaRegistryEntry(
                color=area_config.color,
                icon=area_config.icon,
                id=area.id,
                name=area.name,
                location=area_config.location,
                priority=area_config.priority
            )

            if new_entry.icon is None:
                new_entry.icon = self._get_area_icon(new_entry)

            result[new_entry.id] = new_entry

        return dict(sorted(result.items(), key=lambda x: (-x[1].priority, x[1].name)))

    def _get_area_icon(self, area: AreaRegistryEntry) -> str:
        """ Gets the icon for an area. """
        icon_match = next(filter(lambda x: area.id in x[1] or area.name in x[1], DEFAULT_AREA_ICONS.items()), None)

        if icon_match:
            return icon_match[0]

        return DEFAULT_AREA_ICON


    #--------------------------------------------#
    #       Properties
    #--------------------------------------------#

    @property
    def areas(self) -> dict[str, AreaRegistryEntry]:
        """ Gets the areas. """
        return self._areas


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_id(self, id: str) -> AreaRegistryEntry | None:
        """ Gets an area by id. """
        return self._areas.get(id, None)

    def get_by_name(self, name: str) -> AreaRegistryEntry | None:
        """ Gets an area by name. """
        return next((area for area in self._areas.values() if area.name == name), None)

    def group_by_location(self) -> list[tuple[str, list[AreaRegistryEntry]]]:
        """ Gets a list of areas grouped by location. """
        result: dict[str, list[AreaRegistryEntry]] = {}

        area_config = self._config.areas
        location_config = self._config.area_locations

        for area in self._areas.values():
            location = area_config.get(area.id, area_config.get(area.name, AreaConfig())).location

            if location is None:
                location = "__others__"

            if location not in result:
                result[location] = []

            result[location].append(area)

        return sorted(result.items(), key=lambda x: (-location_config.get(x[0], AreaLocationsConfig()).priority, x[0]), reverse=False)

    def update(self, config: MJ_UserConfig = None) -> None:
        """ Updates the registry. """
        if config:
            self._config = config

        self._areas = self._get_areas(self._hass, self._config)