#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass


#-----------------------------------------------------------#
#       MJ_UserDomainsConfig
#-----------------------------------------------------------#

@dataclass
class MJ_UserDomainsConfig:
    """ A class representing the domains configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    card_size: str
    customize: dict[str, dict]
    customize_global: dict
    exclude: list[str]
    favorites: list[str]
