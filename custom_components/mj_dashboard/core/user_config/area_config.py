#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass, field


#-----------------------------------------------------------#
#       MJ_AreasUserConfig
#-----------------------------------------------------------#

@dataclass
class MJ_AreasUserConfig:
    """ A class representing the areas configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    card_size: str = "300px"
    customize: dict[str, dict] = field(default_factory=dict)
    customize_global: dict = field(default_factory=dict)
    exclude: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)




