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

    card_size: str = "300px"
    customize: dict[str, dict] = field(default_factory=dict)
    customize_global: dict = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    favorites: list[str] = field(default_factory=list)
