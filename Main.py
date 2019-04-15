##############################################################################
## Main.py
##############################################################################
## Description:
## * File contains main method for the Merlin Plotting Tool.

from ConfigurationTypes.CommandLineArgs import CommandLineArgs
from ConfigurationTypes.ConfigurationContainer import ConfigurationContainer
from ConfigurationTypes.EmailConfigurationFile import EmailConfigurationFile
from DirectoryTypes.FileContainer import FileContainer
from DirectoryTypes.FilesAndFoldersContainer import FilesAndFoldersContainer
from DirectoryTypes.FolderContainer import FolderContainer 
import Exceptions.Fatal as Fatals
import Exceptions.NonFatal as NonFatals
import Exceptions.ExceptionAggregator as Aggregate
from PlottingTypes.MerlinPlotter import MerlinPlotter
import Misc.Utilities as util
import os
import sys

#############################################
# main():
# * Main method for application.
#############################################
def main():
    try:
        ################################################
        # Preliminary application checks:
        ################################################
        # Throw Fatal exception if any command line arguments were invalid:
        cmdLineArgs = CommandLineArgs()
        cmdLineArgs.ParseArgs()

        ################################################
        # Attempt to pull in all configuration files:
        ################################################
        allConfigFiles = ConfigurationContainer(cmdLineArgs)
        
        # Get all contents from the configuration files:
        allConfigFiles.GetContents()
        
        ################################################
        ## Generate plots, pdf and email (depending upon command line inputs):
        ################################################
        plotter = MerlinPlotter(cmdLineArgs, allConfigFiles)
        # Print details regarding application execution mode:
        plotter.PrintStartScreen()
        # Only steps that are not prohibited by command line inputs will be executed:
        plotter.Execute()

        # Raise ExceptionAggregator to detail any non-fatal errors that occurred:
        if plotter.HasErrors():
            exceptAgg = plotter.AllErrors
            raise exceptAgg

        # Print exit screen:
        plotter.PrintEndScreen()

    except Fatals.Fatal as err:
        # Print fatal exception and exit if occurred:
        err.HandleAndExit(True)
    except Aggregate.ExceptionAggregator as agg:
        # Print message regarding all non-fatal exceptions and generate logfile if not prevented:
        agg.PrintExceptionScreen()
        agg.GenerateLogFile(cmdLineArgs.ValueDate, cmdLineArgs.RunTime, cmdLineArgs.NoLogFileMode)
    except NonFatals.NonFatal as nonFatal:
        # Print unaggregated NonFatal exception:
        print (nonFatal.Message(True))
    except Exception as err:
        # Print default message if occurred:
        print("The following unhandled exception occurred:")
        print(err.message)
    finally:
        os.system("pause")
        
###########################
# Statement used to execute the main method if this file is directly executed by python interpreter.
###########################
if __name__ == '__main__':
    main()