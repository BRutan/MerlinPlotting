##############################################################################
## FileType.py
##############################################################################
## Description:
## * Abstract base class used to handle all file related functionality.

from abc import ABCMeta, abstractmethod
import DirectoryType
import PathType
import os

__all__ = [ 'FileType' ]

class FileType(DirectoryType.DirectoryType):
    " Class serves as base class for objects representing files. "
    __metaclass__ = ABCMeta
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, path = '', name = ''):
        """
        * Set path to file and file's name in base class.
        """
        self.Path = path
        self.Name = name

    ##########################################################
    ## Public Methods:
    ##########################################################
    @classmethod
    def HandleDuplicates(self, path):
        """
        * Return a filepath with '_#' appended after filename and before extension
        to handle duplicate files.
        Inputs:
        * path: Expecting a string corresponding to file. Will return object if not satisfied.
        """
        # Only work with strings that correspond to files:
        if not isinstance(path, str):
            return path
        elif '.' not in path:
            return path
        # Remove previous duplicate underscores from search path if necessary:
        newPath = path[0 : path.rfind(('_' if '_' in path else '.'))] + self.ExtractExtension(path)
        duplicateCounter = 2
        while os.path.exists(newPath):
            # Append _# to end of file name before extension to handle duplicates:
            newPath = path[0:path.rfind('.')] + '_' + str(duplicateCounter) + path[path.rfind('.'):len(path)]
            duplicateCounter += 1

        return newPath 

    @classmethod
    def GetFinalDuplicateFile(self, path):
        """
        * Return final duplicate file.
        Inputs:
        * path: File path. Expecting string.
        Outputs:
        * currPath: The final duplicate file within the folder.
        """
        # Return object if not string or not a file path:
        if not(isinstance(path, str) and path.rfind('.') != -1):
            return path

        duplicateCounter = 2
        currPath = path
        nextPath = path[0:path.rfind('.')] + '_' + str(duplicateCounter) + path[path.rfind('.'):len(path)]
        while self.CheckPath(currPath) and self.CheckPath(nextPath):
            # Continue to append until no additional duplicates exists:
            currPath = path[0:path.rfind('.')] + '_' + str(duplicateCounter) + path[path.rfind('.'):len(path)] 
            newPath = path[0:path.rfind('.')] + '_' + str(duplicateCounter + 1) + path[path.rfind('.'):len(path)]
            duplicateCounter += 1

        return currPath

    @classmethod
    def HandleLargeFiles(self, path, size = 10):
        """
        * If the final duplicate file is greater than size then output path to new duplicate file.
        Inputs:
        * path: Path to file. Will return if not a true filepath or not a string.
        * size: File size in megabytes.
        Outputs:
        * outputPath: Path to new or current file.
        """
        if not (isinstance(path, str) and '.' in path):
            return path

        outputPath = self.GetFinalDuplicateFile(path)
        # Output to new file if size is greater than 10 MB:
        if self.CheckPath(outputPath) and os.path.getsize(self.GetFinalDuplicateFile(outputPath)) / 1000000 > size:
            outputPath = self.HandleDuplicates(outputPath)

        return outputPath

    def GetContents(self):
        " Abstract method expects to be overwritten in all derived FileTypes. " 
        raise NotImplementedError('This class is an abstract base class.')

    ##########################################################
    ## Accessors:
    ##########################################################
    @property
    def Path(self):
        """
        * Return file's path.
        """
        return self.__path

    @property
    def Name(self):
        """
        * Return name of file.
        """
        return self.__name
    ##########################################################
    ## Mutators:
    ##########################################################
    @Path.setter
    def Path(self, path):
        """
        * Validate and set path.
        Inputs:
        * path: Expecting a string.
        """
        if not isinstance(path, str):
            raise ValueError('Path must be a string.')
        self.__path = path

    @Name.setter
    def Name(self, name):
        """
        * Set the name of the file (to identify in error handling).
        Inputs:
        * name: Expecting a string to identify the name of the file.
        """
        if not isinstance(name, str):
            raise ValueError('Name must be a string.')
        self.__name = name
    