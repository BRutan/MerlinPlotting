##############################################################################
## Observer.py
##############################################################################
## Description:
## * Used to update stored values in containers.

__all__ = ['Observer']

class Observer(object):
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self):
        """ Default constructor. Instantiate generic observer. """
        # Define data which listeners will subscribe to:
        self.__value = ''
        # Define all observer variables:
        self.__observers = []

    ##########################################################
    ## Properties:
    ##########################################################
    @property
    def value(self):
        """  Return stored value from this object. """
        return self.__value

    @value.setter
    def value(self, value):
        """
        * Add object to list of observers, that will have value updated given a change.
        Inputs:
        * value: Update the internal objects's value, and notify all subscribers.
        """
        self.__value = value
        for callback in self.__observers:
            callback(self.__value)
    ##########################################################
    ## Mutators:
    ##########################################################
    def bind_to(self, callback):
        """  Subscribe object's method that will be called when Observer's state changes.
        Inputs:
        * callback: Subscriber object that will receive updates when the Observer's state is changed.
        """
        self.__observers.append(callback)
        
        