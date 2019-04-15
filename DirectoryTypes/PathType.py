##############################################################################
## PathType.py
##############################################################################
## Description:
## * Abstract interface giving derived class Path properties.

from abc import ABCMeta, abstractmethod
import DirectoryType

__all__ = ['PathType']

class PathType(DirectoryType.DirectoryType):
    " Abstract interface giving derived class Path properties. "
    __meta__ = ABCMeta
    ##########################################################
    ## Constructors/"Magic Keywords":
    ##########################################################
    def __init__(self, path = ''):
        """
        * Overloaded Constructor.
        Inputs:
        * path: Expecting a string or a PathType object. 
        """
        self.Path = path

    def __contains__(self, passedString):
        """
        * Overwriting allows one to use 'in' operator on this object.
        """
        if not isinstance(passedString, str):
            raise ValueError('passedString must be a string.')
        return passedString in self.Path
    
    ##########################################################
    ## Properties:
    ##########################################################    
    @property
    def Path(self):
        """
        * Return PDF path.
        """
        return self.__path

    ##########################################################
    ## Setters:
    ##########################################################    
    @Path.setter
    def Path(self, path):
        """
        * Set the PDF Path.
        Inputs:
        * path: Can be a string, PathType object or None.
        """
        if path is None:
            self.__path = ''
        elif isinstance(path, str):
            self.__path = path
        elif isinstance(path, PathType):
            self.__path = path.__path
        else:
            raise ValueError("Path must be a string, PathType object or None.")
        
