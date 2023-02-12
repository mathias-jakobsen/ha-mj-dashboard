#-----------------------------------------------------------#
#       Imports
#-----------------------------------------------------------#

from dataclasses import dataclass
from typing import Optional


#-----------------------------------------------------------#
#       MJ_UserConfig - Domain
#-----------------------------------------------------------#

@dataclass
class DomainConfig:
    """ A class representing the domains configuration. """

    #--------------------------------------------#
    #       Fields
    #--------------------------------------------#

    icon: Optional[str] = None
    priority: int = 1
