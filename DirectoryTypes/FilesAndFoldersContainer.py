##############################################################################
## FilesAndFoldersContainer.py
##############################################################################
## Description:
## * Object handles all file and folder paths, switching depending upon UAT mode.

from DirectoryTypes.FileContainer import FileContainer
from DirectoryTypes.FolderContainer import FolderContainer
import re
import sys

__all__ = ['FilesAndFoldersContainer']

class FilesAndFoldersContainer(object):
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, RunTime, ValueDate, TMinusOne, uatMode = False):
        """ Overloaded constructor. 
        Inputs:
        * RunTime: Must be one of { AM, PM, CAPULA }
        * ValueDate: Creation date for Merlin daily discount factors.
        * TMinusOne: T-1 date.
        * uatMode: True/False to indicate whether application is using UAT paths or not. 
        """
        # Dictionary to Production vs UAT mode (True means UAT paths, False means Production paths):
        self.__FilesAndFolders = { True : { FileContainer : FileContainer(), FolderContainer : FolderContainer() }, False : { FileContainer :  FileContainer(), FolderContainer : FolderContainer() } }
        # Batch Time (AM/PM), T and T-1 dates:
        self.RunTime = RunTime
        self.ValueDate = ValueDate
        self.TMinusOne = TMinusOne
        # Signify whether object is in UATmode (by default, in production):
        self.__UATMode = uatMode

    ##########################################################
    ## Accessors:
    ##########################################################
    def Get(self, Type, mode = None):
        """
        * Return reference to file/folder path container. Will return UAT path if application has been determined to be in UAT mode.
        Inputs:
        * Type: FileContainer/FolderContainer to specify whether path refers to folder or file. 
        """
        if mode is not None and not isinstance(mode, bool):
            raise ValueError("mode must be None or a boolean value.")

        return self.__FilesAndFolders[(self.__UATMode if mode is None else mode)][Type]
        
    ##########################################################
    ## Mutators:
    ########################################################## 
    def ConvertAllSignatures(self):
        """
        * Convert all signatures to appropriate ValueDate and Batch Time. Note: Necessary to perform this before checking paths.
        """
        for group in self.__FilesAndFolders[self.__UATMode].keys():
            self.__FilesAndFolders[self.__UATMode][group].ConvertAllSignatures(self.ValueDate, self.RunTime)

    ##########################################################
    ## Public Methods:
    ##########################################################
    def CheckAllNecessaryPaths(self):
        """
        * Ensure that all necessary paths exist. Note, if application is in UAT mode then will check UAT paths only, and vice versa.
        Outputs:
        * errMessage: Error message indicating which necessary folder paths, files and sheets are missing.
        """
        # Convert all filepaths to adhere to signature system:
        self.ConvertAllSignatures()
        # Ensure all file paths are present:
        errMessage = self.__FilesAndFolders[self.__UATMode][FileContainer].CheckKeyFiles()
        # Ensure all found files have all sheets:
        errMessage += self.__FilesAndFolders[self.__UATMode][FileContainer].CheckKeySheets()
        # Ensure all folder paths are present:
        errMessage += self.__FilesAndFolders[self.__UATMode][FolderContainer].CheckInputPaths()
        
        return errMessage;

    
        
            
