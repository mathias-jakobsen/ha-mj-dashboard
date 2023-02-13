#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass
from typing import Optional


#-----------------------------------------------------------#
#       MJ_UserConfig - Area Locations
#-----------------------------------------------------------#

@dataclass
class AreaLocationsConfig:
    """ A class representing the area locations configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    icon: Optional[str] = None
    priority: int = 1


#-----------------------------------------------------------#
#       MJ_UserConfig - Area
#-----------------------------------------------------------#

@dataclass
class AreaConfig:
    """ A class representing the areas configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    color: Optional[tuple[int, int, int]] = None
    icon: Optional[str] = None
    location: Optional[str] = None
    priority: int = 1
