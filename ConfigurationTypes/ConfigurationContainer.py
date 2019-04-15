##############################################################################
## ConfigurationContainer.py
##############################################################################
## Description:
## * Class aggregates and handles all pertinent configuration files to this application.

from datetime import datetime
from DirectoryTypes.FileType import FileType
import ConfigurationTypes.CommandLineArgs as CmdArgs
from ConfigurationTypes.EmailConfigurationFile import EmailConfigurationFile
from ConfigurationTypes.MerlinGUIWorkbook import MerlinGUIWorkbook
from ConfigurationTypes.PlottingConfigFile import PlottingConfigFile
from ConfigurationTypes.FilepathsFile import FilepathsFile
import Exceptions.Fatal as Fatals

__all__ = [ 'ConfigurationContainer' ]

class ConfigurationContainer(FileType):
    """ Object stores and handles all files used in configuring behavior of this application. """
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, cmdArgs = None):
        """
        * Overloaded constructor. Instantiate all configuration files, set to UAT or Production mode.
        Inputs:
        * isUAT: Expecting a boolean value. The file will use production paths if is not a boolean or is True. 
        * cmdArgs: Expecting a CommandLineArgs object.
        """
        self.__CmdArgs = cmdArgs
        # Store command line arguments in variable, use to overwrite certain members if any command line arguments were passed.
        self.UATMode = (self.__CmdArgs.UATMode if self.__CmdArgs else False)
        # Email configuration file sets subject, recipients and message of generated email:
        self.EmailConfigFile = EmailConfigurationFile(self.UATMode)
        # Plotting configuration file sets each curve that will appear on each plot, as well as daycounts:
        self.PlotConfigs = PlottingConfigFile(self.UATMode)
        # Filepaths.csv stores all file and folder signatures for input and output. Use overwrite path if provided on command line:
        self.Filepaths = FilepathsFile(self.UATMode)
        
    ##########################################################
    ## Public Methods:
    ##########################################################
    def GetContents(self):
        " Pull in all contents of stored configuration files from provided paths: "
        
        files = [ self.EmailConfigFile, self.Filepaths, self.PlotConfigs ]
        error = Fatals.ConfigFilesMissing(callingFunc = 'ConfigurationContainer::GetContents()')

        # Overwrite the PlotConfigs location if provided on command line:
        configFilePath = (None if not self.__CmdArgs else self.__CmdArgs.ConfigFilePath)  
        if configFilePath:
            self.PlotConfigs.Path = configFilePath

        # Ensure that the local \\Configs\\ folder is present:
        parentFolder = self.ConvertSignature('{LocalPath}\\Configs\\')
        if not self.CheckPath(parentFolder):
            error.Add(Fatals.ConfigFilesMissing(callingFunc = 'ConfigurationContainer::__init__()', specific = 'The \\Configs\\ folder is missing (%s)' % parentFolder))
            raise error

        ####################
        # Pull in all files, store files that could not be pulled:
        ####################
        for file in files:
            try:
                file.GetContents()
            except Fatals.ConfigFilesMissing as err:
                error.Merge(err)
    
        # Raise exception if failed to get any files:
        if error.HasErrors:
            raise error

        # Overwrite using command line arguments if necessary:
        self.__CmdArgsOverwrite()

    ##########################################################
    ## Properties/Setters:
    ##########################################################
    @property
    def __CmdArgs(self):
        """
        * Return access to the command args object.
        """
        return self.__cmdArgs
    @property
    def UATMode(self):
        """
        * Return indicatino of the UAT mode of this application.
        """
        return self.__UATMode
    @__CmdArgs.setter
    def __CmdArgs(self, cmdArgs):
        """
        * Set the command argument object.
        Inputs:
        * cmdArgs: Expecting a CommandLineArgs object. If not passed then this object will be None.
        """
        if isinstance(cmdArgs, CmdArgs.CommandLineArgs):
            self.__cmdArgs = cmdArgs
        else:
            self.__cmdArgs = None     
    @UATMode.setter
    def UATMode(self, isUAT):
        """
        * Set the UAT mode for configuration files.
        Inputs:
        * isUAT: Expecting boolean. If not boolean then gets set to False by default.
        """
        if isinstance(isUAT, bool):
            self.__UATMode = isUAT
        else:
            self.__UATMode = False

    ##########################################################
    ## Private Helpers:
    ##########################################################
    def __CmdArgsOverwrite(self):
        """
        * Overwrite relevant items with command line argument provided items if required.
        """
        # Return if command line arguments weren't provided:
        if not self.__CmdArgs:
            return

        # Overwrite items with command line argument inputs:
        pdfPath = self.__CmdArgs.PDFPath
        pngOutPath = self.__CmdArgs.PNGOutputPath

        if pdfPath:
            self.Filepaths.PDFOutputLocation = pdfPath 
        if pngOutPath:
            self.Filepaths.PNGOutputLocation = pngOutPath

        
        

        

            
                
        