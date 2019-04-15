##############################################################################
## FilepathsFile.py
##############################################################################
## Description:
## * Object stores all input and output file paths. 

import csv
from DirectoryTypes.FileType import FileType
import Exceptions.Fatal as Fatals
import re
import sys

class FilepathsFile(FileType):
    " Object stores all input and output file paths. "
    ##########################################################
    ## Class Methods:
    ##########################################################
    def __init__(self, UATMode = False):
        """
        * Overloaded constructor. 
        Inputs:
        * UATMode: Expecting a boolean value. The file will use production paths if is not a boolean or is True.
        * pathOverWrite: Expecting a string filepath.
        """
        # This file expects to live in the "...\MerlinPlotting\Configs\" folder:
        UATMode = (False if not isinstance(UATMode, bool) else UATMode)
        path = self.ConvertSignature("{LocalPath}\\Configs\\{UAT/Prod}\\Filepaths.csv", UAT = UATMode)
        name = self.ExtractFileName(path)
        (super() if sys.version_info[0] > 2 else super(FilepathsFile, self)).__init__(path, name)
        self.FincadCurvesLocation = ''
        self.PDFOutputLocation = ''
        self.PNGOutputLocation = ''
        # List stores all invalid entries in the file:
        self.__InvalidCategories = []
                    
    ##########################################################
    ## Class Methods:
    ##########################################################
    def GetContents(self):
        """
        * Attempt to pull in contents from the Filepaths.csv file.
        """
        # Reset the invalid categories:
        self.__InvalidCategories = []
        ##########################
        # Ensure that file is in expected location:
        ##########################
        if not FileType.CheckPath(self.Path):
            raise Fatals.ConfigFilesMissing(callingFunc = 'FilepathsFile::GetContents()', fileName = self.Name, filePath = self.Path)
    
        with open(self.Path, 'r') as f:
            reader = list(csv.reader(f))
            # Expecting <Category>,<Path>:
            for row in reader:
                self.__CategoryToPath(row[0], row[1])

        if len(self.__InvalidCategories) > 0:
            message = 'The following file or folder path categories were invalid:\n%s' % (','.join(self.__InvalidCategories))
            raise Fatals.ConfigFilesMissing(callingFunc = 'FilepathsFile::GetContents()', fileName = self.Name, filePath = self.Path, specific = message)

    def __CategoryToPath(self, category, path):
        """
        * Set this object's variable based upon category.
        Inputs:
        * category: Expecting a string. If no match then will be added to the invalid entries list
        that will be used to generate an exception.
        * path: Expecting a string path or path signature.
        """
        # Exit immediately if value is not a string:
        if not isinstance(category, str) or not isinstance(path, str):
            return

        path = path.strip()

        if re.compile('fincad', re.IGNORECASE).match(category):
            self.FincadCurvesLocation = path
        elif re.compile('pdfoutput', re.IGNORECASE).match(category):
            self.PDFOutputLocation = path
        elif re.compile('pngoutput', re.IGNORECASE).match(category):
            self.PNGOutputLocation = path
        else:
            self.__InvalidCategories.append(category)