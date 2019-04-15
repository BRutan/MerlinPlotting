##############################################################################
## PathSubscriber.py
##############################################################################
## Description:
## * Subscriber that contains path information with Observer (to be stored in containers).

import PathType

__all__ = ['PathSubscriber']

class PathSubscriber(PathType.PathType):
    " Subscriber that contains path information with Observer (to be stored in containers). "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, observer):
        """
        * Overloaded constructor. Initialize the stored data and subscribe to passed observer object.
        Inputs:
        * observer: Observer object that will update this object's state given change in its state.
        """
        # Path for file or folder:
        self.path = ''
        # Observer object that this object will subscribe to:
        self.data = observer
        # Bind this object to the observer:
        self.data.bind_to(self.update_path)

    ##########################################################
    ## Mutators:
    ##########################################################
    def update_path(self, newPath):
        """
        * Update this object's stored data using new data.
        """
        self.Path = newPath
\