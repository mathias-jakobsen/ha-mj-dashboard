#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass, field


#-----------------------------------------------------------#
#       MJ_UserEntitiesConfig
#-----------------------------------------------------------#

@dataclass
class MJ_UserEntitiesConfig:
    """ A class representing the domains configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    customize: dict[str, dict] = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    favorites: list[str] = field(default_factory=list)
