##############################################################################
## DirectoryContainerBase.py
##############################################################################
## Description:
## * Base class for File/Folder container types.

from abc import ABCMeta, abstractmethod
from DirectoryTypes.FileType import FileType

__all__ = ['LocationBase']

class DirectoryContainerBase(FileType):
    __metaclass__ = ABCMeta
    ##########################################################
    ## Abstract Methods:
    ##########################################################
    @abstractmethod
    def ConvertAllSignatures(self, ValueDate, RunTime):
        """
        * Abstract method needed to be overriden in derived classes. Converts all locations with signatures:
        """
        pass