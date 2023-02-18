#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass, field


#-----------------------------------------------------------#
#       MJ_UserDomainsConfig
#-----------------------------------------------------------#

@dataclass
class MJ_UserDomainsConfig:
    """ A class representing the domains configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    customize: dict[str, dict] = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    favorites: list[str] = field(default_factory=list)
