##############################################################################
## DirectoryType.py
##############################################################################
## Description:
## * Abstract base class handles functionality for directories.

from abc import ABCMeta, abstractmethod
from datetime import date, datetime
import os
import re
import Misc.Utilities as util
import shutil
import sys

__all__ = [ 'DirectoryType' ]

class DirectoryType(object):
    " Abstract base class handles functionality for all directories. "
    # Folder pattern is used to test if a path corresponds to a valid folder. 
    folderPattern = '[A-Z]:\/[0-9a-zA-Z_\/\s]*'
    # Make this class abstract:
    __metaclass__ = ABCMeta
    ##########################################################
    ## Public Methods:
    ##########################################################
    @classmethod
    def ConvertSignature(self, path, **kwargs):
        """
        * Return path with signatures replaced by relevant values given value date and run time.
        Mandatory inputs:
        * path: Path that needs converting.
        Optional Inputs
        * ForOutput: Clean the filepath for output, by removing invalid characters (
        * ValueDate: Date to use in conversion. Can be string (convertible to datetime), datetime or date.
        * RunTime: String containing runtime. Expected to be "AM"/"PM".
        * CurveName: Name of curve for plotting. 
        * PlotName: Name of plot title.
        * Color: Plot color.
        * UAT: Regarding whether application is in UAT or Production mode.
        Output:
        * path: Updated path with signature tokens filled.
        """
        # Convert variadic arguments to useable form, and handle unsuitable types being passed:

        ValueDate = kwargs.get('ValueDate', None)
        if isinstance(ValueDate, str) and util.StringIsDate(ValueDate):
            ValueDate = datetime.strptime(ValueDate, '%m/%d/%Y')
        elif not isinstance(ValueDate, datetime) and not isinstance(ValueDate, date):
            ValueDate = None
        
        RunTime = kwargs.get('RunTime', None)
        RunTime = ('' if not isinstance(RunTime, str) else RunTime)
        CurveName = kwargs.get('CurveName', None)
        CurveName = ('' if not isinstance(CurveName, str) else CurveName)
        PlotName = kwargs.get('PlotName', None)
        PlotName = ('' if not isinstance(PlotName, str) else PlotName)
        Color = kwargs.get('Color', None)
        Color = ('' if not isinstance(Color , str) else Color)
        UAT = kwargs.get('UAT', None)
        UAT = (None if not isinstance(UAT, bool) else UAT)
        ForOutput = kwargs.get('ForOutput', False)

        if ValueDate:
            if '{MM}' in path:
                path = path.replace('{MM}', ('0' if ValueDate.month < 10 else '') + str(ValueDate.month))
            if '{DD}' in path:
                path = path.replace('{DD}', ('0' if ValueDate.day < 10 else '') + str(ValueDate.day))
            if '{YY}' in path:
                path = path.replace('{YY}', str(ValueDate.year % 100))
            if '{YYYY}' in path:
                path = path.replace('{YYYY}', str(ValueDate.year))
        if RunTime and '{RunTime}' in path:
            path = path.replace('{RunTime}', RunTime)
        if CurveName and '{CurveName}' in path:
            path = path.replace('{CurveName}', CurveName)
        if PlotName and '{PlotName}' in path:
            path = path.replace('{PlotName}', PlotName)
        if Color and '{Color}' in path:
            path = path.replace('{Color}', Color)
        if '{LocalPath}' in path:
            path = path.replace('{LocalPath}', os.path.abspath(os.path.dirname(sys.argv[0])))
        if not (UAT is None) and '{UAT/Prod}' in path:
            path = path.replace('{UAT/Prod}', ('UAT' if UAT else 'Production')) 

        # Clean the output path of illegal characters if using to write to file system:
        if ForOutput:
            illegalChars = ['<','>','|','{','}','?','*']
            for char in illegalChars:
                path = path.replace(char, '')
        
        return path

    @classmethod
    def ConvertPathToISIS(self, path):
        """
        * Convert paths from using 'K:\Operations\Oberon' to '\\isis\common\Common\Operations'.
        Inputs:
        * path: Expecting a folder or file path string.
        Outputs:
        * Returns path using isis convention. Returns path if not a string or file\folder path.
        """
        if not isinstance(path, str): 
            return path
        if '/' not in path and "\\" not in path:
            return path
        path = self.FixPath(path)        

        if re.match('^K:/Operations/[0-9a-fA-F/]*', path):
            path = path.replace('K:/Operations/', '//isis/common/Operations/' )
       
        return path

    @classmethod
    def AppendHyphenIfNecessary(self, path):
        """
        * Append hyphen as final character to folder path if necessary.
        Inputs:
        * path: Folder path. Expecting string.
        Outputs:
        * Returns path if not a folder path, otherwise returns path with hyphen appended if necessary.
        """
        # Return original object if not a string.
        if not isinstance(path, str):
            return path
        # Replace backslashes with forward slashes:
        path = path.replace('\\','/')
        # Return path if a file path or not a true directory:
        if '.' in path or not '/' in path:
            return path
        # Return folder path with hyphen as final character if necessary:
        return path + ('/' if path[len(path) - 1] != '/' else '')

    @classmethod
    def CheckPath(self, path):
        """
        * Determine if file or folder path exists.
        Inputs:
        * path: folder or file path to check.
        Outputs:
        * True if folder/file exists, false if otherwise.
        """
        if os.path.exists(path):
            return True
        return False

    @classmethod
    def CopyToTempFolder(self, listOfFiles, tempFolder = '{LocalPath}/Temp/', simpleRename = False):
        """
        * Copy all folder contents to temporary folder.
        Inputs:
        * listOfFiles: List of file paths to copy.
        * tempFolder: Specify temporary folder. Supports signature system in ConvertSignature(). 
        By default writes to Temp folder in local path. Will be created if does not exist.
        * simpleRename: True if want to replace names with simple names (ex "1.png"). 
        Output:
        * oldToNewMap: Map s.t. { Old Path -> Temp Path }.
        """
        # Grab enclosing folder name if a file was passed as the temporary folder:
        tempFolder = self.ConvertSignature(tempFolder)
        tempFolder = self.ExtractFolderName(tempFolder)
        tempFolder = self.AppendHyphenIfNecessary(tempFolder)
        tempFolder = self.FixPath(tempFolder)
        self.CreateFolderIfDoesNotExist(tempFolder)

        tempFolderPaths = []
        if simpleRename:
            tempNum = 1
            for targetFile in listOfFiles:
                tempFolderPaths.append('%s%s%s' % (tempFolder, str(tempNum), self.ExtractExtension(targetFile)))
                tempNum += 1
        else:
            tempFolderPaths = ['%s%s' % (tempFolder, self.ExtractFileName(filePath)) for filePath in listOfFiles]

        # Copy all files to temporary folder:
        targetIndex = 0
        oldToNewMap = {}
        for targetTempFile in tempFolderPaths:
            currFile = listOfFiles[targetIndex]
            shutil.copy2(currFile, targetTempFile)
            oldToNewMap[currFile] = targetTempFile
            targetIndex += 1
        
        # Return list containing list of generated temporary files or map of { Old Path -> New Path}:
        return oldToNewMap

    @classmethod
    def CreateFolderIfDoesNotExist(self, path):
        """
        * Create folder if does not exist.
        Inputs:
        * path: folder to create if does not exist, or file 
        that is contained in a folder that want to create if does not exist.
        """
        # Extract directory from passed filepath:
        path = self.ExtractFolderName(path)
        # Create folder if does not exist already:
        if not os.path.exists(path):
            os.mkdir(path)

    @classmethod
    def DeleteFolder(self, path):
        """
        * Recursively delete all folder contents at path. Skip if file was passed or folder does not exist.
        """
        # Replace backslashes with forward slashes:
        path = self.FixPath(path)
        if '.' in path or not self.CheckPath(path):
            return
        for root, directories, filenames in os.walk(path):
            # Delete all file names:
            for filename in filenames:
                if self.CheckPath(root + filename):
                    os.remove(root + filename)
            # Recursively empty out all folders:
            for folder in directories:
                self.DeleteFolder(folder)
            # Delete the directory:
            shutil.rmtree(root)

    @classmethod
    def ExtractExtension(self, path):
        """
        * Extract file extension (with '.') from passed path. 
        Inputs:
        * path: Expecting a string corresponding to file. Will return object if not satisfied.
        """
        # Return object if non-string was passed:
        if not isinstance(path, str):
            return path
        elif '.' not in path:
            return path
        return path[path.rfind('.'):len(path)]

    @classmethod
    def ExtractFileName(self, path):
        """
        * Extract file from passed path.
        Inputs:
        * path: Expecting a string corresponding to file. Will return object if not satisfied.
        """
        # Return original object if non-string was passed:
        if not isinstance(path, str):
            return path
        # Replace backslashes with forward slashes:
        path = path.replace('\\','/')
        if '.' not in path or '/' not in path:
            return path
        return path[path.rfind('/') + 1:len(path)]

    @classmethod
    def ExtractFolderName(self, path):
        """
        * Return enclosing folder of passed file, or return blank string if
        path is invalid (has no hyphens).
        """
        # Return blank string if not a directory:
        if '/' not in path:
            return ''
        return DirectoryType.AppendHyphenIfNecessary(path[0:path.rfind('/')])

    @classmethod
    def FixPath(self, path):
        """
        * Return filepath with backslashes replaced with forward slashes.
        Inputs:
        * path: Expecting a string corresponding to file. Will return object if not satisfied.
        """
        if not isinstance(path, str):
            return path
        return path.replace('\\','/')

    @classmethod
    def IsFolder(self, path, raiseIfFail = False):
        """
        * Indicate whether passed path is a folder.
        Inputs:
        * path: Expecting a string.
        * raiseIfFail: If True then will raise an exception if fail or return the path if does not fail.
        """
        path = self.AppendHyphenIfNecessary(path)
        m = re.search(DirectoryType.folderPattern, path)
        if m is None and raiseIfFail:
            raise ValueError
        elif m is None:
            return False
        else:
            return path
        return True
