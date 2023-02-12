#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass, field


#-----------------------------------------------------------#
#       MJ_UserConfig - Exclude
#-----------------------------------------------------------#

@dataclass
class ExcludeConfig:
    """ A class representing the exclude configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    areas: list[str] = field(default_factory=list)
    domains: list[str] = field(default_factory=list)
    entities: list[str] = field(default_factory=list)