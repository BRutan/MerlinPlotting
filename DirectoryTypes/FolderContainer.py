##############################################################################
## FolderContainer.py
##############################################################################
## Description:
## * Object handles all folder paths for this application.

from DirectoryTypes.DirectoryContainerBase import DirectoryContainerBase
from DirectoryTypes.Observer import Observer
import os
from DirectoryTypes.PathSubscriber import PathSubscriber

__all__ = ['FolderContainer']

class FolderContainer(DirectoryContainerBase):
    " Object aggregates folderpath observers to be used throughout the application. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self):
        """ Default constructor. Instantiate new folder container. """
        ## Input Folders:
        # RAVEN generated Merlin curves location:
        self.FincadCurvesLocationSignature = Observer()
        ## Output Folders:
        # Final PDF output location:
        self.PDFOutputLocationSignature = Observer()
        # PNG plot output location:
        self.PNGOutputLocationSignature = Observer()
        # Dictionary to hold all input folders (need to check that they exist):
        # Bind all observers to the stored paths:
        self.__AllInputFolders = { "Fincad Curves" : PathSubscriber(self.FincadCurvesLocationSignature) } 
        
    ##########################################################
    ## Mutators:
    ##########################################################
    def ConvertAllSignatures(self, ValueDate, RunTime):
        """ Convert all folderPaths to use signature. """
        
        self.FincadCurvesLocationSignature.value = DirectoryContainerBase.ConvertSignature(self.FincadCurvesLocationSignature.value, ValueDate, RunTime)
        self.PDFOutputLocationSignature.value = DirectoryContainerBase.ConvertSignature(self.PDFOutputLocationSignature.value, ValueDate, RunTime)
        self.PNGOutputLocationSignature.value = DirectoryContainerBase.ConvertSignature(self.PNGOutputLocationSignature.value, ValueDate, RunTime)

    ##########################################################
    ## Public Methods:
    ##########################################################
    def CheckInputPaths(self):
        """ Ensure that all required input paths exist.
        Output:
        * missingPaths: String contains all missing configuration files.
        """
        missingPaths = ''
        # Ensure that all input paths exist:
        for pathName in self.__AllInputFolders.keys():
            # Get containing folder if signature was passed:
            folderPath = self.__AllInputFolders[pathName]
            if not CheckContainingFolder(folderPath):
                missingPaths += pathName + '\n'
        missingPaths = ('\nFollowing paths do not exist:' if missingPaths else '') + missingPaths + ('\n' if missingPaths else '')
    
        return missingPaths

    def CheckContainingFolder(self, path):
        """ Ensure that folder containing passed file at path exists or if a folder path was provided that it exists.
        Inputs:
        * path: File or folder path to check.
        """
        # Remove signature aspects from path:
        if '{' in path:
            path = path[0:path.find('{') - 1]
        if '.' in path:
            path = path[0:path.find('.') - 1]
        # Determine if folder exists:
        if os.path.exists(path):
            return True
        return False
        
        