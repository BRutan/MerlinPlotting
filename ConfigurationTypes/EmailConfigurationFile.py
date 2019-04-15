##############################################################################
## EmailConfigurationFile.py
##############################################################################
## Description:
## * Class handles the EmailConfig.csv file that sets aspects of the PNG email.

import csv
from DirectoryTypes.FileType import FileType
import Exceptions.Fatal as Fatals
import sys

__all__ = ['EmailConfigurationFile']

class EmailConfigurationFile(FileType):
    " Object handles the email configuration file used in setting properties of the generated PNG email. "
    def __init__(self, UATMode):
        """ 
        * Overloaded constructor 
        Inputs:
        * UATMode: Expecting a boolean value. The file will use production paths if is not a boolean or is True.
        """
        # This file expects to live in the "...\MerlinPlotting\Configs\" folder:
        path = FileType.ConvertSignature('{LocalPath}\\Configs\\{UAT/Prod}\\EmailConfig.csv', UAT = UATMode)
        name = FileType.ExtractFileName(path)
        if sys.version_info[0] > 2:
            super().__init__(path, name)
        else:
            super(EmailConfigurationFile, self).__init__(path, name)
        self.Recipients = None
        self.Subject = ''

    ##########################################################
    ## Mutators:
    ##########################################################
    def GetContents(self):
        " Get contents of email configuration file. "
        
        ##########################
        # Ensure that file is in expected location:
        ##########################
        if not FileType.CheckPath(self.Path):
            raise Fatals.ConfigFilesMissing(callingFunc = 'EmailConfigurationFile::GetContents()', fileName = self.Name, filePath = self.Path)
        
        self.Recipients = []
        try:
            # Pull in contents from file:
            with open(self.Path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if 'Recipients' in row[0]:
                        # Add all configured email recipients:
                        for elem in row[1:len(row)]:
                            if elem.strip() not in self.Recipients:
                                self.Recipients.append(elem)
                    elif 'Subject' in row[0] and len(row) > 1:
                        self.Subject = row[1]
        except Exception as err:
            # Raise fatal exception (that will be aggregated downstream) if any issues occurred:
            raise Fatals.ConfigFilesMissing(callingFunc = 'EmailConfigurationFile::GetContents()', fileName = self.Name, filePath = self.Path, specific = err.message)