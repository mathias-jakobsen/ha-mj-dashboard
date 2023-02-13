#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from ..const import DASHBOARD_URL, PARSER_KEYWORD
from .config import MJ_Config
from .logger import LOGGER
from .registry import get_registry
from homeassistant.core import Event, HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util.yaml import loader
from typing import Callable
import io, jinja2, os


#-----------------------------------------------------------#
#       Constants
#-----------------------------------------------------------#

EVENT_LOVELACE_UPDATE = "lovelace_updated"


#-----------------------------------------------------------#
#       Variables
#-----------------------------------------------------------#

_lovelace_listener: Callable = None
_old_loader: Callable = None
_should_reload: bool = True


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
    global _old_loader, _should_reload

    if _old_loader is None:
        return setup(hass, config)

    LOGGER.debug("Reloading the modified YAML loader.")
    loader.load_yaml = _get_load_yaml(hass, config)
    _should_reload = True

def remove() -> None:
    """ Removes the modified YAML loader. """
    global _lovelace_listener, _old_loader, _should_reload

    if _old_loader is None:
        return

    LOGGER.debug("Removing the modified YAML loader.")
    loader.load_yaml = _old_loader
    if _lovelace_listener:
        _lovelace_listener()
    _lovelace_listener = None
    _old_loader = None
    _should_reload = True


#-----------------------------------------------------------#
#       Event Handlers
#-----------------------------------------------------------#

async def _async_on_lovelace_update(e: Event) -> None:
    """ Triggered when lovelace is updated. """
    global _should_reload

    if e.data.get("url_path", None) == DASHBOARD_URL:
        _should_reload = True


#-----------------------------------------------------------#
#       Private Functions
#-----------------------------------------------------------#

def _get_load_yaml(hass: HomeAssistant, config: MJ_Config) -> None:
    """ Gets the YAML loader. """
    jinja = jinja2.Environment(loader=jinja2.FileSystemLoader("/"))

    def load_yaml(filename: str, secrets: loader.Secrets = None, args: dict = {}) -> loader.JSON_TYPE:
        global _should_reload

        try:
            is_lovelace_gen = False

            with open(filename, encoding="utf-8") as file:
                if file.readline().lower().startswith(PARSER_KEYWORD):
                    is_lovelace_gen = True

            if is_lovelace_gen:
                stream = io.StringIO(jinja.get_template(filename).render({**args, **get_registry(hass, config, _should_reload)}))
                stream.name = filename
                if _should_reload:
                    _should_reload = False
                return loader.parse_yaml(stream, secrets)
            else:
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