##############################################################################
## MerlinPlottingExcept.py
##############################################################################
## Description:
## * Exception base class for all exceptions in this application.
## In general, a Merlin Plotting exception has a "Header Message" giving a brief
## detailing of the issue that will be output to stdout on application close.
## The "Specific Message" will be output to the LogFile.

from abc import ABCMeta, abstractmethod
from datetime import datetime
import sys
from Misc.Utilities import StringIsDate

__all__ = ['MerlinPlottingExcept']

class MerlinPlottingExcept(BaseException):
    " Base class for both fatal and non-fatal Merlin Plotting exceptions. "
    __metaclass__ = ABCMeta
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, callingFunc, specific = '', timestamp = datetime.now()):
        """
        * Overloaded constructor.
        Inputs:
        * callingFunc: String details where exception was thrown. Expected to contain class/module information.
        * specific: Expecting string consisting of message that was part of thrown default exception at runtime.
        * timeStamp: Datetime object detailing when exception was thrown.
        """
        self.CallingFunction = callingFunc
        self.SpecificMessage = specific
        self.TimeStamp = timestamp
    
    ##########################################################
    ## Class Methods:
    ##########################################################    
    @abstractmethod
    def Message(self, granular = False):
        """
        * This function must be overwritten in derived classes in order for them to 
        be instantiated.
        """
        pass
    ##########################################################
    ## Accessors:
    ##########################################################
    @property
    def CallingFunction(self):
        " Return function where this exception occurred. "
        return self.__callingFunc
    @property
    def SpecificMessage(self):
        " Return specific error message that was thrown at runtime (comes from the various default exception categories). "
        return self.__specific
    @property
    def TimeStamp(self):
        " Return time when this exception occurred. "
        return self.__timeStamp

    def TimeStampToStr(self, time = False):
        " Return timestamp in string form, with or without time added. "
        return self.TimeStamp.strftime(("%m/%d/%Y %H:%M:%S" if time else "%m/%d/%Y")) 

    ##########################################################
    ## Mutators:
    ##########################################################
    @CallingFunction.setter
    def CallingFunction(self, callingFunc):
        """
        * Set function where exception occurred.
        Inputs:
        * callingFunc: Expecting a string detailing the class and function where exception occurred, or None.
        """
        if callingFunc is None:
            # Instantiate to blank string:
            self.__callingFunc = ''
        elif isinstance(callingFunc, str):
            self.__callingFunc = callingFunc
        else:    
            raise ValueError("CallingFunction must be a string or None.")

    @SpecificMessage.setter
    def SpecificMessage(self, message):
        """
        * Set the specific message that was detailed with thrown error at runtime.
        Inputs:
        * message: Expecting a string or None.
        """
        if message is None:
            # Instantiate the message to default:
            self.__specific = ''
        elif isinstance(message, str):
            self.__specific = message
        else:
            raise ValueError("SpecificMessage must be a string or None.")

    @TimeStamp.setter
    def TimeStamp(self, time):
        """
        Set time when exception occurred.
        Inputs:
        * time: datetime object or string that can be converted to a datetime object.
        """
        if isinstance(time, str): 
            # Ensure that string can be 
            if not StringIsDate(time, True):
                raise ValueError("Could not convert TimeStamp to a datetime object. Format is MM/DD/YYYY HH:MM:SS")
            # Convert string to datetime object:
            self.__timeStamp = datetime.strptime(time, "%m/%d/%Y %H:%M:%S")
        elif not isinstance(time, datetime):
            raise ValueError("TimeStamp must be either a datetime object or convertible string.")
        self.__timeStamp = time
