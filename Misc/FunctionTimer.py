##############################################################################
## FunctionTimer.py
##############################################################################
## Description:
## * Simple timer class for determining processing function processing time.

__all__ = [ 'FunctionTimer' ]

import time

class FunctionTimer:
    " Used to calculate function execution length. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self):
        """ Default constructor. Instantiate new timer object and set time to 0. """
        self.t_0 = 0

    def Start(self):
        """ Start stop watch. """
        self.t_0 = time.time()

    def Stop(self):
        """ Stop stop watch and return execution time. """
        temp = time.time() - self.t_0
        self.t_0 = 0
        return temp