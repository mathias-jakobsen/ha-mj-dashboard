#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass


#-----------------------------------------------------------#
#       MJ_AreasUserConfig
#-----------------------------------------------------------#

@dataclass
class MJ_AreasUserConfig:
    """ A class representing the areas configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    card_size: str
    customize: dict[str, dict]
    customize_global: dict
    exclude: list[str]
    locations: list[str]




