#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass


#-----------------------------------------------------------#
#       MJ_UserEntitiesConfig
#-----------------------------------------------------------#

@dataclass
class MJ_UserEntitiesConfig:
    """ A class representing the domains configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    customize: dict[str, dict]
    exclude: list[str]
    favorites: list[str]
