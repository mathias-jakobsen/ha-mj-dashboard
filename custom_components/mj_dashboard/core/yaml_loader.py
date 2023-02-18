#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DASHBOARD_URL, PARSER_KEY_GLOBAL, PARSER_KEYWORD
from .config import MJ_Config
from .logger import LOGGER
from .registry import MJ_Registry
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import loader
from typing import Callable
import io, jinja2, json, os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

EVENT_LOVELACE_UPDATE = "lovelace_updated"


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_lovelace_listener: Callable = None
_old_loader: Callable = None
_registry: MJ_Registry = None


#-----------------------------------------------------------#
#       Setup
#-----------------------------------------------------------#

def setup(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Sets up the YAML loader. """
    global _lovelace_listener, _old_loader

    if _old_loader is None:
        _old_loader = loader.load_yaml

    LOGGER.debug("Setting up the modified YAML loader.")
    loader.load_yaml = _get_load_yaml(hass, config)
    loader.SafeLoader.add_constructor("!include", _include_yaml)
    _lovelace_listener = hass.bus.async_listen(EVENT_LOVELACE_UPDATE, _async_on_lovelace_update)

def reload(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Reloads the YAML loader. """
    global _old_loader, _registry

    if _old_loader is None:
        return setup(hass, config)

    LOGGER.debug("Reloading the modified YAML loader.")
    loader.load_yaml = _get_load_yaml(hass, config)
    _registry = None

def remove() -> None:
    """ Removes the modified YAML loader. """
    global _lovelace_listener, _old_loader, _registry

    if _old_loader is None:
        return

    LOGGER.debug("Removing the modified YAML loader.")
    loader.load_yaml = _old_loader
    if _lovelace_listener:
        _lovelace_listener()
    _lovelace_listener = None
    _old_loader = None
    _registry = None


#-----------------------------------------------------------#
#       Event Handlers
#-----------------------------------------------------------#

async def _async_on_lovelace_update(e: Event) -> None:
    """ Triggered when lovelace is updated. """
    global _registry

    if e.data.get("url_path", None) == DASHBOARD_URL:
        _registry = None


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _get_load_yaml(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Gets the YAML loader. """
    def jinja_filter_as_json(value):
        return json.dumps(value)

    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("/"))
    jinja.filters["asjson"] = jinja_filter_as_json

    def load_yaml(filename: str, secrets: loader.Secrets = None, args: dict = {}, parse_jinja: bool = True) -> loader.JSON_TYPE:
        global _registry

        try:
            if parse_jinja:
                with open(filename, encoding="utf-8") as file:
                    if file.readline().lower().startswith(PARSER_KEYWORD):
                        if _registry is None:
                            _registry = { PARSER_KEY_GLOBAL: MJ_Registry.from_config(hass, config) }

                        stream = io.StringIO(jinja.get_template(filename).render({**args, **_registry}))
                        stream.name = filename
                        return loader.parse_yaml(stream, secrets)

            with open(filename, encoding="utf-8") as file:
                return loader.parse_yaml(file, secrets)
        except loader.yaml.YAMLError as exc:
            LOGGER.error(str(exc))
            raise HomeAssistantError(exc)
        except UnicodeDecodeError as exc:
            LOGGER.error("Unable to read file %s: %s", filename, exc)
            raise HomeAssistantError(exc)

    return load_yaml


#-----------------------------------------------------------#
#       Safeline Loaders
#-----------------------------------------------------------#

def _include_yaml(ldr, node):
    """ Allows for including YAML files with variables. """
    args = {}
    if isinstance(node.value, str):
        fn = node.value
    else:
        fn, args, *_ = ldr.construct_sequence(node)
    fname = os.path.abspath(os.path.join(os.path.dirname(ldr.name), fn))
    try:
        return loader._add_reference(loader.load_yaml(fname, ldr.secrets, args=args), ldr, node)
    except FileNotFoundError as exc:
        LOGGER.error("Unable to include file %s: %s", fname, exc)
        raise HomeAssistantError(exc)