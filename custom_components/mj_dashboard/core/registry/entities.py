#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ...const import DOMAIN
from ..user_config import MJ_UserConfig
from .areas import MJ_AreaRegistry, MJ_AreaRegistryEntry
from .domains import MJ_DomainRegistryEntry
from dataclasses import dataclass
from homeassistant.const import ATTR_DEVICE_CLASS, ATTR_FRIENDLY_NAME, ATTR_UNIT_OF_MEASUREMENT
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_devices
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_registry import async_get as async_get_entities


#-----------------------------------------------------------#
#       MJ_EntityRegistryEntry
#-----------------------------------------------------------#

@dataclass
class MJ_EntityRegistryEntry:
    """ A class representing an entity entry. """
    domain: str
    entity_id: str
    hidden: bool = False
    area_id: str | None = None
    device_class: str | None = None
    device_id: str | None = None
    entity_category: EntityCategory | None = None
    icon: str | None = None
    name: str | None = None
    unit_of_measurement: str | None = None


#-----------------------------------------------------------#
#       EntityRegistry
#-----------------------------------------------------------#

class MJ_EntityRegistry:
    """ A class representing an entity registry. """

    #--------------------------------------------#
    #       Constructor
    #--------------------------------------------#

    def __init__(self, hass: HomeAssistant, areas: MJ_AreaRegistry, config: MJ_UserConfig):
        self._areas: MJ_AreaRegistry = areas
        self._config: MJ_UserConfig = config
        self._entities: dict[str, MJ_EntityRegistryEntry] = self._get_entities(hass, config)
        self._hass: HomeAssistant = hass


    #--------------------------------------------#
    #       Iterator
    #--------------------------------------------#

    def __iter__(self):
        for entry in self._entities.values():
            yield entry


    #--------------------------------------------#
    #       Private Methods
    #--------------------------------------------#

    def _get_entities(self, hass: HomeAssistant, config: MJ_UserConfig) -> dict[str, MJ_EntityRegistryEntry]:
        """ Gets a dictionary containing the entity entries. """
        device_registry = async_get_devices(hass).devices
        entity_registry = async_get_entities(hass).entities
        result = {}

        for state in hass.states.async_all():
            if state.entity_id in config.entities.exclude:
                continue

            new_entry = MJ_EntityRegistryEntry(
                area_id=None,
                device_class=state.attributes.get(ATTR_DEVICE_CLASS, ""),
                device_id=None,
                domain=state.domain,
                entity_category=None,
                entity_id=state.entity_id,
                hidden=False,
                name=state.attributes.get(ATTR_FRIENDLY_NAME, ""),
                unit_of_measurement=state.attributes.get(ATTR_UNIT_OF_MEASUREMENT, None))

            if entity := entity_registry.get(state.entity_id):
                if entity.disabled:
                    continue

                if entity.platform == DOMAIN:
                    continue

                if entity.device_id:
                    device = device_registry.get(entity.device_id)

                    if device.disabled:
                        continue

                    new_entry.area_id = device.area_id
                    new_entry.device_id = device.id

                if entity.area_id:
                    new_entry.area_id = entity.area_id

                if new_entry.device_class == None:
                    new_entry.device_class = entity.device_class if entity.device_class else entity.original_device_class if entity.original_device_class else ""

                if new_entry.entity_category is None:
                    new_entry.entity_category = entity.entity_category

                new_entry.hidden = entity.hidden

                if new_entry.icon is None:
                    new_entry.icon = entity.icon or entity.original_icon

                if new_entry.name is None:
                    new_entry.name = entity.name or entity.original_name

                if new_entry.unit_of_measurement is None:
                    new_entry.unit_of_measurement = entity.unit_of_measurement

            result[new_entry.entity_id] = new_entry

        return result


    #--------------------------------------------#
    #       Public Methods
    #--------------------------------------------#

    def get_by_area(self, area: MJ_AreaRegistryEntry | str | list[MJ_AreaRegistryEntry | str], domain: str | list[str] = None, device_class: str | list[str] = None) -> list[MJ_EntityRegistryEntry]:
        """ Gets a list of entities by one or more areas. """
        if not isinstance(area, list):
            area = [area]

        areas = [self._areas.get_by_id(area) or self._areas.get_by_name(area) if type(area) == str else area for area in area]
        area_ids = [area.id for area in areas]
        device_classes = [device_class] if type(device_class) == str else device_class
        domains = [domain] if type(domain) == str else domain
        result = []

        for entity in self._entities.values():
            if entity.area_id not in area_ids:
                continue

            if domains is not None and entity.domain not in domains:
                continue

            if device_classes is not None and (not entity.device_class or entity.device_class not in device_class):
                continue

            result.append(entity)

        return result

    def get_by_device_class(self, domain: str | MJ_DomainRegistryEntry, *device_classes: str) -> list[MJ_EntityRegistryEntry] | tuple[str, list[MJ_EntityRegistryEntry]]:
        """ Gets a list of entities by one or more device classes. """
        result = {}

        for entity in self.get_by_domain(domain):
            if len(device_classes) > 0 and entity.device_class not in device_classes:
                continue

            if entity.device_class not in result:
                result[entity.device_class] = []

            result[entity.device_class].append(entity)

        if len(device_classes) == 1:
            return result[device_classes[0]] if device_classes[0] in result else []

        return sorted(result.items(), key=lambda x: (x[0] == "", x[0]))

    def get_by_domain(self, *domains: str | MJ_DomainRegistryEntry) -> list[MJ_EntityRegistryEntry]:
        """ Gets a list of entity by one or more domains. """
        domains = [domain if isinstance(domain, str) else domain.id for domain in domains]
        return [entity for entity in self._entities.values() if entity.domain in domains]

    def get_by_id(self, id: str) -> MJ_EntityRegistryEntry | None:
        """ Gets an entity by id. """
        return self._entities.get(id, None)

    def update(self, config: MJ_UserConfig = None) -> None:
        """ Updates the registry. """
        if config:
            self._config = config

        self._entities = self._get_entities(self._hass, self._config)