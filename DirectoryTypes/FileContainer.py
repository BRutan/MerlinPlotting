##############################################################################
## FileContainer.py
##############################################################################
## Description:
## * Object handles all file paths for this application.

import os
import re
from DirectoryTypes.PathSubscriber import PathSubscriber
from DirectoryTypes.Observer import Observer
# from openpyxl import load_workbook
from DirectoryTypes.DirectoryContainerBase import DirectoryContainerBase

__all__ = ['FileContainer']

class FileContainer(DirectoryContainerBase):
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self):
        """
        * Default constructor. Instantiate new container to store production/uat file paths. 
        """
        ## Input Files:
        # File contains all Plot Titles ('PlotBatchList sheet'), Merlin Curve name to Plot Title map and whether or not to plot T-1 in addition to T (Overlays), and daycount conventions (XCCY_DayCnt):
        self.ConfigFileSignature = Observer()
        # Container has all files and necessary sheets that need to be checked (if file is not a workbook then list will be blank):
        self.__AllKeyFilesAndSheets = { 'Configuration File' : (PathSubscriber(self.ConfigFileSignature), [ ]) }
        # Container contains all files that could not be found:
        self.__MissingFiles = []

    ##########################################################
    ## Mutators:
    ##########################################################
    def ConvertAllSignatures(self, ValueDate, RunTime):
        """
        * Convert all filepaths to use signature.
        """
        self.ConfigFileSignature.value = DirectoryContainerBase.ConvertSignature(self.ConfigFileSignature.value, ValueDate, RunTime) 
        
    ##########################################################
    ## Public Methods:
    ##########################################################
    def CheckKeyFiles(self):
        """
        * Ensure that all stored files exist. Output error message indicating which files are missing, and update the internal missing files list:
        Outputs:
        * missingFiles: Message indicating which files are missing from this container.
        """
        missingFiles = ''
        # Reset the missing files list:
        self.__MissingFiles = []
        for fileName in self.__AllKeyFilesAndSheets.keys():
            # Convert signature for application file:
            filePath = self.__AllKeyFilesAndSheets[fileName][0].path
            # Add to error message
            if not os.path.exists(filePath):
                missingFiles += '\n' + fileName
                self.__MissingFiles.append(fileName)
        missingFiles = ('\nFollowing files are missing:' if missingFiles else '') + missingFiles + ('\n' if missingFiles else '')
    
        return missingFiles

    def CheckKeySheets(self):
        """
        * Ensure that each present file has all necessary sheets.
        Outputs:
        * missingSheets: Message indicating which sheets are missing for each given file.
        """
        missingSheets = ''
        temp = ''
        for fileName in self.__AllKeyFilesAndSheets.keys():
            # Only search Excel workbooks that were found:
            filePath = self.__AllKeyFilesAndSheets[fileName][0].path
            if fileName not in self.__MissingFiles and re.search('.xl*', filePath):
                workbook = load_workbook(self.__AllKeyFilesAndSheets[fileName][0].path, True, False, True, False, False)
                temp = ''
                for sheet in self.__AllKeyFilesAndSheets[fileName][1]:
                    if sheet not in workbook:
                        temp += (fileName + ': { ' if fileName not in missingSheets else ',') + sheet
                if temp:
                    temp += ' }\n'
                missingSheets += temp
        # Return error message:
        return ('\nFollowing sheets are missing for each file:' if missingSheets else '') + missingSheets