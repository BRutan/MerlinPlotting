##############################################################################
## Grid.py
##############################################################################
## Description:
## * Define generic grid list object to be used in conjunction with Observer() class.

__all__ = ['Grid']

class Grid(object):
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, observer):
        """
        * Initialize the stored data and subscribe to passed observer object.
        """
        self.AllData = []
        self.data = observer
        self.data.bind_to(self.update_data)   
    ##########################################################
    ## Mutators:
    ##########################################################
    def update_data(self, newData):
        """
        * Update this object's stored data using new data.
        """
        self.AllData = newData