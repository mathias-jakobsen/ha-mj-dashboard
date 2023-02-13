#-----------------------------------------------------------#
#       General
#-----------------------------------------------------------#

DOMAIN = "mj_dashboard"
NAME = "MJ Dashboard"
PACKAGE_NAME = f"custom_components.{DOMAIN}"
PLATFORMS = []


#-----------------------------------------------------------#
#       Dashboard
#-----------------------------------------------------------#

DASHBOARD_FILE_PATH = f"custom_components/{DOMAIN}/lovelace/ui-lovelace.yaml"
DASHBOARD_URL = f"{DOMAIN.replace('_', '-')}"


#-----------------------------------------------------------#
#       Resources
#-----------------------------------------------------------#

RESOURCES_PATH = f"custom_components/{DOMAIN}/resources"
RESOURCES_STATIC_PATH = f"/{DOMAIN}/resources"


#-----------------------------------------------------------#
#       Themes
#-----------------------------------------------------------#

THEMES_FILE_PATH_SOURCE = f"custom_components/{DOMAIN}/themefiles/{DOMAIN}.yaml"
THEMES_FILE_PATH_DESTINATION = f"{DOMAIN}/"


#-----------------------------------------------------------#
#       Translations
#-----------------------------------------------------------#

TRANSLATIONS_PATH = f"custom_components/{DOMAIN}/lovelace/translations"


#-----------------------------------------------------------#
#       YAML Parser
#-----------------------------------------------------------#

PARSER_KEYWORD = f"# {DOMAIN}"
PARSER_KEY_GLOBAL = "mj"
