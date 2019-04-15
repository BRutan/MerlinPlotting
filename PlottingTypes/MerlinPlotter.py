##############################################################################
## MerlinPlotter.py
##############################################################################
## Description:
## * Object handles all aspects related to generating the final Merlin PNG plots,
## pdf and email (depending upon command line inputs).
 
import datetime
import Exceptions.Fatal as Fatals
import Exceptions.NonFatal as NonFatals
from Exceptions.ExceptionAggregator import ExceptionAggregator
from ConfigurationTypes.CommandLineArgs import CommandLineArgs
from ConfigurationTypes.ConfigurationContainer import ConfigurationContainer
from ConfigurationTypes.PlottingConfigFile import PlottingConfigFile, CurveConfig
from Exceptions.ExceptionAggregator import ExceptionAggregator
from DirectoryTypes.FilesAndFoldersContainer import FilesAndFoldersContainer
from DirectoryTypes.FileContainer import FileContainer
from DirectoryTypes.FileType import FileType
from DirectoryTypes.FolderContainer import FolderContainer
from DirectoryTypes.Observer import Observer
from PlottingTypes.ForwardRatePlot import ForwardRatePlot
from random import randint
from multiprocessing import pool
import reportlab.lib.pagesizes as sizes
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, SimpleDocTemplate
import os
from shutil import copy2
import win32com.client as win32
import threading
import time
import Misc.Utilities as util
import sys

__all__ = ['MerlinPlotter']

class MerlinPlotter(FileType):
    " Object aggregates all forward rate plots that will be generated and delegates functionality for generating pdf and email. "
    ##########################################################
    ## Class Static Variables:
    ##########################################################
    # Use fixed width and height for each image (will be scaled when outputting PDF):
    plotPDFWidth = 200
    plotPDFHeight = 150
    ##########################################################
    ## Constructors/"Magic Functions":
    ##########################################################
    def __init__(self, commandLine, allConfigFiles):
        """
        * Overloaded constructor. 
        Inputs:
            * commandLine: Object containing all command line arguments. Must be provided at object construction.
        Optional Inputs:
            * plottingConfigFile: Plotting configuration file that determines which merlin curves appear on which plots and the associated
            daycount conventions used to calculate forward rates. 
            * fileAndFolderContainer: FilesAndFoldersContainer object containing all production/uat paths.  
        """
        # Dictionary contains all plots that will be generated (using contents of plotting configuration file):
        self.__AllPlots = {}
        # Object contains all configuration files:
        self.AllConfigs = allConfigFiles
        # Store all command line arguments that will alter object functionality:
        self.CommandArgs = commandLine
        # Instantiate the nonfatal exception aggregator:
        self.AllErrors = ExceptionAggregator()
        # Store temporary folder that will get deleted when plotter closes:
        self.__TempFolder = ''
        # Store final output path signature for PDF file, will be grabbed from ConfigurationContainer:
        self.__finalPDFSignature = ''
        # Store actually generated PDF:
        self.__completedPDF = ''

    def __exit__(self, exc_type, exc_value, traceback):
        """
        * Called when object is destroyed. Ensures that temporary folder is deleted.
        """
        self.DeleteFolder(self.__TempFolder)

    ##########################################################
    ## Class Methods:
    ##########################################################
    def Execute(self):
        """
        * Execute all key functions. Steps will be skipped if prohibited by command line inputs (see CommandLineArgs).
        """
        if self.CommandArgs.TestImagePath:
            # Generate test image and skip all other steps:
            self.GenerateTestPNG()
        else:
            # Load all plots from the configuration file:
            self.LoadAllPlots()
            # Generate all plot images
            self.GenerateAllPlotImages()
            # Output PDF to stored path:
            self.GeneratePDF()
            # Generate email with plots if not prohibited:
            self.GenerateEmailWithPlots()
        # Raise the stored ExceptionAggregator if any issues occurred:
        if self.AllErrors.HasErrors:
            raise self.AllErrors

    ##########################################################
    ## Key Steps:
    ##########################################################
    def LoadAllPlots(self):
        """
        * Create each plot object necessary for given application run time using 
        Note: this method will be skipped if --pnginput <Path> was specified on command line.
        """
        # Skip this step if not required to generated plots (based upon command line inputs):
        if self.CommandArgs.PNGInputPath:
            return

        # Get all application attributes from the file and folder container:
        ValueDate = self.CommandArgs.ValueDate
        RunTime = self.CommandArgs.RunTime
        TMinusOne = self.CommandArgs.TMinusOne
        # Input files are Merlin generated discount factor curves:
        inputPath = self.AllConfigs.Filepaths.FincadCurvesLocation
        # Output file is PNG to configured path signature dependent upon value date:
        outputPath = self.AllConfigs.Filepaths.PNGOutputLocation
        
        self.PrintStep("Loading all plot configurations", False)
        # Reset the plots dictionary:
        self.__AllPlots = {}
        # Object points to all plot configurations:
        plotConfigs = self.AllConfigs.PlotConfigs.ConfiguredPlots        

        ########################
        # Generate all plot objects that will be generated in GenerateAllPlotImages():
        ########################
        for plotName in plotConfigs.keys():
            firstCurve = list(plotConfigs[plotName].keys())[0]
            # Only initialize plots that are required for current application runtime:
            if plotConfigs[plotName][firstCurve].RunTime == RunTime:
                # If TPath and TMinusOnePath were set on command line then will override the Merlin Curves path when plot is generated: 
                self.__AllPlots[plotName] = ForwardRatePlot(plotConfigs[plotName], inputPath, outputPath, plotName, ValueDate, TMinusOne, TPath = self.CommandArgs.TPath, TMinusOnePath = self.CommandArgs.TMinusOnePath)
        
        self.PrintStep("Done", True)

    def GenerateAllPlotImages(self):
        """
        * Generate all plot PNG images using stored ForwardRatePlots() synchronously.
        Note: this method will be skipped if --pnginput <Path> was specified on command line.
        """
        # Skip step if prohibited by command line:
        if self.CommandArgs.PNGInputPath:
            return

        self.PrintStep("Generating all plot images", False)
        
        ########################
        # Generate all plot images:
        ########################
        for plotName in self.__AllPlots.keys():
            try:
                self.__AllPlots[plotName].GenerateImage()
            except Fatals.Fatal as fatal:
                # Pass fatal exception immediately to main method:
                self.PrintStep("Failed to generate PNGs.", True)
                raise fatal
            except NonFatals.NonFatal as nonfatal:
                # Add non-fatal exception to aggregator:
                self.AllErrors.Add(nonfatal)
      
        self.PrintStep("Done", True)

    def GeneratePDF(self):
        """
        * Output all generated PNG plots to single PDF.
        Note: this method will be skipped if the --nopdf flag was specified at command line.
        """
        # Skip step if prohibited by command line:
        if self.CommandArgs.NoPDFMode:
            return

        finalPNGS = []
        temp = []
        #####################
        # Use overwrite PNG folder if provided and exists:
        #####################
        if self.CommandArgs.PNGInputPath and FileType.CheckPath(self.CommandArgs.PNGInputPath):
            finalPNGs = ['%s%s' % (self.CommandArgs.PNGInputPath, fileName) for fileName in os.listdir(self.CommandArgs.PNGInputPath) if 'MerlinCurveGraph' in fileName and '.png' in fileName]
        else:
            # Arrange the paths in the order that the corresponding plots appear in the plotting configuration file:                  
            plotsInOrder = self.AllConfigs.PlotConfigs.PlotsInOrder
            for name in plotsInOrder:
                for plot in self.__AllPlots.keys():
                    if name == self.__AllPlots[plot].PlotTitle and self.__AllPlots[plot].FinalOutputPath:
                        finalPNGS.append(FileType.ConvertPathToISIS(self.__AllPlots[plot].FinalOutputPath))
                        break    
        
        # Skip if no PNGS were generated or could not be found in provided location:
        if len(finalPNGS) == 0:
            return

        # Reset the pdf output path:
        self.__completedPDF = ''

        # Set the output path using stored path object:
        pdfOutputPath = self.AllConfigs.Filepaths.PDFOutputLocation
        pdfOutputPath = FileType.ConvertSignature(pdfOutputPath, ValueDate = self.CommandArgs.ValueDate, RunTime = self.CommandArgs.RunTime)
        # Append "_#" before extension to handle duplicate files:
        pdfOutputPath = FileType.HandleDuplicates(pdfOutputPath)
        #####################
        # Output all of the plots into a single pdf with fixed positioning:
        #####################
        # Create enclosing folder for pdf if does not exist:
        self.CreateFolderIfDoesNotExist(self.ExtractFolderName(pdfOutputPath))

        self.PrintStep("Generating PDF", False)
        xBorder = 50
        yBorder = 30 
        plotCount = 0
        imgScale = 1.7
        try:
            pageType = sizes.landscape(sizes.A4)
            # Alter width and height of plot to ensure it can fit on the sheet:
            xMax, yMax = pageType
            plotWidth = min(MerlinPlotter.plotPDFWidth * imgScale, xMax)
            plotHeight = min(MerlinPlotter.plotPDFHeight * imgScale, yMax)
            xStart = xBorder
            yStart = yMax - (plotHeight + yBorder)
            pdf = canvas.Canvas(pdfOutputPath, pageType)
            x = xStart
            y = yStart
            for pngPath in finalPNGS:
                # Set image position:
                if plotCount == 0:
                    # Add new sheet to PDF if already loaded 4 charts to sheet:
                    x = xStart
                    y = yStart
                elif plotCount == 1:
                    # Place second chart to right of first chart:
                    x += plotWidth + xBorder
                elif plotCount == 2:
                    # Place third chart on bottom left:
                    x = xStart
                    y -= plotHeight + yBorder
                elif plotCount == 3:
                    # Place final chart on bottom right:
                    x += plotWidth + xBorder
                pdf.drawImage(pngPath, x, y, plotWidth, plotHeight)
                plotCount += 1
                plotCount %= 4
                # Add new page if added 4 plots:
                if plotCount == 0:
                    pdf.showPage()
            pdf.save()
            self.__completedPDF = pdfOutputPath

            self.PrintStep("Done", True)

        except Exception as err:
            self.PrintStep("Failed to generate PDF.", True)
            self.AllErrors.Add(NonFatals.FailedToGeneratePDF(pdfOutputPath, 'MerlinPlotter::GeneratePDF()', specific = err.message))

    def GenerateEmailWithPlots(self):
        """
        * Generate outlook email with all generated plots attached.
        Note: this method will be skipped if --noemail flag was specified at command line.
        """
        ########################
        # Skip if prohibited by command line arguments:
        ########################
        if self.CommandArgs.NoEmailMode:
            return

        fullPaths = []
        runTime = self.CommandArgs.RunTime
        valueDate = self.CommandArgs.ValueDate
        ########################
        # Use PNGS located in passed overwrite folder if provided at command line:
        ########################
        if self.CommandArgs.PNGInputPath and FileType.CheckPath(self.CommandArgs.PNGInputPath):
            # Use pngs located in overwrite folder:
            pngFolder = os.listdir(self.CommandArgs.PNGInputPath)
            # Filter out non-png files:
            pngs = [fileName for fileName in pngFolder if '.png' in fileName]
            # Use full paths 
            fullPaths = [FileType.AppendHyphenIfNecessary(self.CommandArgs.PNGInputPath) + fileName for fileName in pngs]
        else:
            # Use pngs generated this session.
            # Arrange the paths in the order they appear in the plotting configuration file:
            plotsInOrder = self.AllConfigs.PlotConfigs.PlotsInOrder
            fullPaths = []
            for name in plotsInOrder:
                for plot in self.__AllPlots.keys():
                    if name == self.__AllPlots[plot].PlotTitle and self.__AllPlots[plot].FinalOutputPath:
                        fullPaths.append(FileType.ConvertPathToISIS(self.__AllPlots[plot].FinalOutputPath))
                        break      
        
        # Exit if no plots were created or available:
        if len(fullPaths) == 0:
            return

        ########################
        # Generate Email with plots:
        ########################
        self.PrintStep("Generating email", False)
        
        # Generate html string used to attach all PNGs to message:        
        textBody = 'Please review Merlin graphs in e-mail attachment.'
        htmlImages = ''

        for png in fullPaths:
            htmlImages += '<br><br><img src="%s"><br/><br/>' % (png)
        
        # Generate html string to link the output PDF if generated during this session:
        pdfLink = ''
        if not self.CommandArgs.NoPDFMode and self.CheckPath(self.__completedPDF):
            pdfLink = "<a href='%s'>Link to PDF</a>" % (self.__completedPDF) 
            
        htmlString = '<html><body>%s<p>%s</p>%s</body></html>' % (pdfLink, textBody, htmlImages)

        # Create email, embed all graphs and link to generated PDF:
        try:
            recipients = self.AllConfigs.EmailConfigFile.Recipients
            subject = self.AllConfigs.EmailConfigFile.Subject
            outlook = win32.Dispatch('Outlook.Application')
            # Generate new email (underlying enumeration value is 0 for Outlook email):
            email = outlook.CreateItem(0)
            # Insert colon between recipients:
            email.To = ';'.join(recipients)
            # Attach all images to the email that will get placed inline in the message:
            email.Subject = FileType.ConvertSignature(subject, ValueDate = valueDate, RunTime = runTime)
            email.HtmlBody = htmlString
            # Display message without sending:
            email.Display(False)

            self.PrintStep("Done", True)

        except Exception as err:
            # Add exception to aggregator if could not display the email:
            self.PrintStep("Failed to generate email.", True)
            self.AllErrors.Add(NonFatals.OutlookFailed('MerlinPlotter::GenerateEmailWithPlots()', specific = err.message))

    ##########################################################
    ## Accessors:
    ##########################################################    
    @property
    def AllConfigs(self):
        """
        * Provide access to the ConfigurationContainer object containing all files necessary to run
        this application.
        """
        return self.__configFile
    @property
    def AllErrors(self):
        " Return access to stored ExceptionAggregator object. "
        return self.__NonFatals
    @property
    def CommandArgs(self):
        " Return access to the stored command line arguments object. "
        return self.__commandArgs

    def HasErrors(self):
        " Indicate if any issues occurred when plotting. " 
        return self.AllErrors.HasErrors

    def PlottingErrors(self):
        " Provide access to the ExceptionAggregator object. "
        return self.AllErrors

    ##########################################################
    ## Mutators:
    ##########################################################
    @AllErrors.setter
    def AllErrors(self, exceptionAgg):
        """
        * Set the ExceptionAggregator object.
        Inputs:
        * exceptionAgg: Expecting None or an ExceptionAggregator object. If None is passed then
        will instantiate new ExceptionAggregator.
        """
        if exceptionAgg is None:
            # Instantiate new instance using stored CommandLineArgs.
            self.__NonFatals = ExceptionAggregator(self.CommandArgs)
        elif isinstance(exceptionAgg, ExceptionAggregator):
            self.__NonFatals = exceptionAgg
        else:
            raise ValueError('AllErrors must be an ExceptionAggregator object, or None.')

    @AllConfigs.setter
    def AllConfigs(self, allConfigFiles):
        """
        * Set the ConfigurationContainer object.
        Input:
        * allConfigFiles: Expecting a ConfigurationContainer object.
        """
        if isinstance(allConfigFiles, ConfigurationContainer):
            self.__configFile = allConfigFiles
        else:
            raise ValueError('AllConfigs must be a ConfigurationContainer object.')

    @CommandArgs.setter
    def CommandArgs(self, commandLine):
        """ 
        * Set the command line argument module. Must be provided at object construction or else 
        an exception will be thrown.
        """
        if not isinstance(commandLine, CommandLineArgs):
            raise ValueError('CommandArgs must be a CommandLineArgs object.')
        else:
            self.__commandArgs = commandLine

    ##########################################################
    ## Auxilliary Functions:
    ##########################################################
    def GenerateTestPNG(self):
        """
        * Generate single graph using 4 curves with fixed configurations.
        """
        self.PrintStep("Generating test image", False)
        inputLoc = self.AllConfigs.Filepaths.FincadCurvesLocation

        configRows = {'GMOAUD-6-1500NY' : CurveConfig(Curve = 'GMOAUD-6-1500NY'), 'GMOAUD-3-1500NY' : CurveConfig(Curve = 'GMOAUD-3-1500NY'), 'GMOAUD-0-1500NY' : CurveConfig(Curve = 'GMOAUD-0-1500NY') }
        for config in configRows.keys():
            configRows[config].PlotT1 = True
            configRows[config].RunTime = 'PM'

        configRows['GMOAUD-6-1500NY'].FwdRateConv = 180
        configRows['GMOAUD-3-1500NY'].FwdRateConv = 90
        configRows['GMOAUD-0-1500NY'].FwdRateConv = 1
    
        testGraph = ForwardRatePlot(configRows, inputLoc, self.CommandArgs.TestImagePath, 'AUD - GMO', self.CommandArgs.ValueDate, self.CommandArgs.TMinusOne)
        ########################
        # Attempt to output test image to path set at command line:
        ########################        
        try:            
            testGraph.GenerateImage()
            self.PrintStep("Done", True)
        except NonFatals.NonFatal as err:
            self.PrintStep("Failed to generate test image", True)
            self.AllErrors.Add(err)

    def PrintStartScreen(self):
        """
        * Print application mode description to stdout.
        """
        print('####################################################################')
        print('## MERLIN PLOTTING                                                ##')
        print('####################################################################')
        print(self.CommandArgs.ApplicationModeString())
        print('####################################################################')

    def PrintEndScreen(self):
        """
        * Print application end message to stdout.
        """
        print('####################################################################')
        print('Finished executing the required steps.')
        print('####################################################################')

    def PrintStep(self, step, end = False):
        """
        * Print current step being run.
        Inputs:
        * step: Expecting a string.
        * end: Expecting a boolean.
        """
        if not isinstance(step, str) or not isinstance(end, bool):
            raise ValueError('step must be string, end must be boolean.')
        time.sleep(1)
        step = (step + '\n**********************************' if end else '**********************************\n' + step)
        print(step)
        
    def GenerateAllPlotImages_Async_Threads(self):
        """
        * Generate all plot PNG images using Threading library.
        """
        # Skip this step if folder containing PNGS was provided:
        if self.CommandArgs.PNGInputPath:
            return
        
        threads = {}
        for plotName in self.__AllPlots.keys():
                plot = self.__AllPlots[plotName]
                threads[plotName] = threading.Thread(target=plot.GenerateImage)
        
        for plotName in threads.keys():
            threads[plotName].start()
        
        for plotName in threads.keys():
            threads[plotName].join()

    def GenerateAllPlotImages_Async_Processes(self): 
        """
        * Generate all plot PNG images using stored ForwardRatePlots() asynchronously.
        Note that if PNG folder was specified on command line then this will be skipped.
        """
        # Skip this step if folder containing PNGS was provided:
        if self.CommandArgs.PNGInputPath:
            return        

        processes = {}
        # Put each plot object into own process:
        for plotName in self.__AllPlots.keys():
            plot = self.__AllPlots[plotName]
            processes[plotName] = pool.Process(target=plot.GenerateImage)
        
        # Start all processes:
        for process in processes.values():
            process.start()
        
        # Join all after starting:
        for process in process.values():
            process.join()

        # Check each thread for errors:
        for plot in processes.keys():
            if self.__AllPlots[plot].ErrorMessage != '':
                errorMessage += self.__AllPlots[plot].ErrorMessage
        
        return '' 