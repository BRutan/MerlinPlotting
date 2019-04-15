##############################################################################
## CommandLineArgs.py
##############################################################################
## Description:
## * Object handles command line arguments.

import argparse
import datetime
from DirectoryTypes.FileType import FileType
from DirectoryTypes.DirectoryType import DirectoryType
import Exceptions.Fatal as Fatals
import re
import sys
from Misc.Utilities import FirstMatchIndex, GetTMinusOne, StrToBool, StringIsDate

class CommandLineArgs(FileType):
    """     
    Object handles all aspects related to getting and setting command line arguments.
        State objects:
        **** Mandatory:
        * ValueDate: Expecting convertible string to date object.
        * RunTime: Expecting one of {AM, PM, CAPULA}.
        **** Optional:
        * ConfigFilePath: Passing '--configpath <PATH>' will override the path to the Curve Plotting Configuration.csv file.
        * TPath: Passing '--tpath <PATH>' will override the T Merlin Curve path with provided one.
        * T1Path: Passing '--t1path <PATH>' will override the T-1 Merlin Curve path with provided one.
        * PDFOutput: Passing '--pdfoutput <PATH>' will override the path for PDf output.
        * PNGInputPath: Passing '--pnginput <PATH>' will cause graph generation to be skipped and PDF to be generated using PNGs located in provided folder path.
        * PNGOutputPath: Passing '--pngoutput <PATH>' will cause PNGs to be output to provided path.
        * NoEmail: Passing '--noemail' will prevent email from being generated.
        * NoPDF: Passing '--nopdf' will prevent the PDF from being generated.
        * NoLog: Passing '--nolog' will prevent log file from being generated.
        * TestImage: Passing '--TestImage <PATH>' will generate single test image using current ForwardRatePlot settings to provided folder or file path.
        * T1Override: Passing '--t1 <Date>' will change the default T-1 date to provided one.
        * UATMode: Passing '--uat' will display application mode as UAT, and will by default use UAT paths listed in the Filepaths.csv file, otherwise use
        the passed paths.
    """
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self):
        """
        * Default constructor. Initialize new command line argument container that handles pulling in all mandatory and
        optional inputs from the command line.
        """
        (super() if sys.version_info[0] > 2 else super(CommandLineArgs, self)).__init__()
        
    ##########################################################
    ## Class Methods:
    ##########################################################
    def ParseArgs(self):
        """
        * Parse all arguments on command line, raise exception if any failed. 
        """
        desc = "Generate Forward Rate PNGS for each Merlin generated file at predetermined path in PlottingConfigs.py, generate PDF with those PNGs and email."
        parser = argparse.ArgumentParser(prog = 'MerlinPlotting', description=desc, usage='%(prog)s vd {MM/DD/YYYY} batch {AM/PM/CAPULA} [options]')
        parser.add_argument('ValueDate', type=self.__StrToDate, help='Value date for Merlin Curve discount factors.', nargs=1)
        parser.add_argument('Batch', type=str, choices = ['AM','PM','CAPULA'], help="Batch time. Must be one of {AM/PM/CAPULA}.", nargs=1)
        parser.add_argument('--configpath', type = str, dest='ConfigFilePath', help="Override path to Curve Plotting Config.csv file.", nargs=1)
        parser.add_argument('--uat', dest='UATMode', help='Set application to use UAT paths.', action='store_true')
        parser.add_argument('--pnginput', type = str, dest='PNGInputPath', help='If provided, then application will use PNGS in provided folder to generate the PDF.', nargs=1)
        parser.add_argument('--pngoutput', type = str, dest='PNGOutputPath', help='If provided, then application will output generated PNGs to this folder.', nargs=1)
        parser.add_argument('--noemail', dest = 'NoEmail', help='Skip generating email.', action='store_true')
        parser.add_argument('--nopdf', dest = 'NoPDF', help='Skip generating PDF.', action='store_true')
        parser.add_argument('--nolog', dest = 'NoLog', help='Skip generating log file.', action = 'store_true')
        parser.add_argument('--pdfoutput', type = str, dest = 'PDFPath', help='Override the default pdf output path.', nargs=1)
        parser.add_argument('--testpath', type = str, dest = 'TestImagePath', help = 'Generate single test image to path for fixed ValueDate using current ForwardRatePlot settings and exit.', nargs=1)
        parser.add_argument('--t1', type = self.__StrToDate, dest = 'TMinusOne', help ="T-1 date override. By default is first previous business day from ValueDate.", nargs=1) 
        parser.add_argument('--tpath', type=str, dest='TPath', help="Override path to T Merlin discount factor curves. Path must exist.", nargs=1)
        parser.add_argument('--t1path', type=str, dest = 'TMinusOnePath', help ="Overwrite path to T-1 Merlin discount factor curves. Path must exist.", nargs=1) 
        
        error = Fatals.CommandLineErrors("CommandLineArgs()")
        # Pull in all command line arguments and input into the CommandLineArgs class:
        args = parser.parse_known_args()
        error.InvalidArgs = args[1]
        
        ################################
        # Validate all command line arguments:
        ################################
        argDict = {}
        # Set all mandatory arguments (ValueDate and RunTime):
        argDict['ValueDate'] = (args[0].ValueDate[0], 'ValueDate')
        argDict['RunTime'] = (args[0].Batch[0], 'RunTime')
        # Set all optional arguments:
        argDict['ConfigFilePath'] = ((args[0].ConfigFilePath[0] if args[0].ConfigFilePath else None), '--configpath')
        argDict['PNGInputPath'] = ((args[0].PNGInputPath[0] if args[0].PNGInputPath else None), '--pnginput')
        argDict['PNGOutputPath'] = ((args[0].PNGOutputPath[0] if args[0].PNGOutputPath else None), '--pngoutput')
        argDict['UATMode'] = (args[0].UATMode, '--uat')
        argDict['NoPDFMode'] = (args[0].NoPDF, '--nopdf')
        argDict['NoEmailMode'] = (args[0].NoEmail, '--noemail')
        argDict['NoLogFileMode'] = (args[0].NoLog, '--nolog')
        argDict['PDFPath'] = ((args[0].PDFPath[0] if args[0].PDFPath else None), '--pdfoutput')
        argDict['TMinusOne'] = ((args[0].TMinusOne[0] if args[0].TMinusOne else None), '--t1')
        argDict['TMinusOnePath'] = ((args[0].TMinusOnePath[0] if args[0].TMinusOnePath else None), '--t1path')
        argDict['TPath'] = ((args[0].TPath[0] if args[0].TPath else None), '--tpath')
        argDict['TestImagePath'] = ((args[0].TestImagePath[0] if args[0].TestImagePath else None), '--testpath')

        # Instantiate all of this object's properties to defaults:
        self.__ConfigFilePath = None
        self.__NoPDFMode = None
        self.__NoEmailMode = None
        self.__NoLogFileMode = None
        self.__PNGInputPath = None
        self.__PNGOutputPath = None
        self.__PDFPath = None
        self.__RunTime = None
        self.__UATMode = None
        self.__TMinusOne = None
        self.__TMinusOnePath = None
        self.__TestImagePath = None
        self.__TPath = None
        self.__ValueDate = None
        
        ################################
        # Set all of this object's properties, collect incorrectly passed parameters:
        ################################
        derivedProperties = sorted([key.split('__')[1] for key in vars(self).keys() if 'CommandLineArgs' in key])
        for property in derivedProperties:
            try:
                setattr(self, property, argDict[property][0])
            except ValueError as err:
                error.Add((argDict[property][1], "'" + err.message + "'"))

        ################################
        # Pass fatal exception to main method if any command line arguments failed to meet standards:
        ################################
        if error.HasErrors:
            raise error

    def ApplicationModeString(self):
        """
        * Return message indicating how application will be executed.
        """
        messageString = ''
        # Print mandatory parameters (application must have specified ValueDate and RunTime, T-1 date will be default if not specified):
        messageString = 'Value Date: %s\n' % self.ValueDate.strftime('%m/%d/%y')
        messageString += 'T-1 Date: %s\n' % self.TMinusOne.strftime('%m/%d/%y')
        messageString += 'Run Time: %s\n' % self.RunTime
        if self.TestImagePath:
            # If generating a test image then only display the output path:
            messageString += '\nGenerating test image to \n%s.' % self.TestImagePath
            return messageString

        # Print optional parameters (UAT/Production mode, overridden PNG folder path, and whether or not log file will be generated): 
        messageString += ('UAT' if self.UATMode else 'Production') + ' Mode'
        messageString += ('\nLog file will be skipped.' if self.NoLogFileMode else '')
        messageString += ('\nNo PDF will be generated.' if self.NoPDFMode else '')
        messageString += ('\nNo email will be generated.' if self.NoEmailMode else '')
        messageString += ('\nOutputting PNGS to location: \n%s.' % self.PNGOutputPath if self.PNGOutputPath else '')
        messageString += ('\nUsing Configuration File located in \n%s.' % self.ConfigFilePath if self.ConfigFilePath else '')
        messageString += ('\nUsing T Merlin Curves located in \n%s.' % self.TPath if self.TPath else '')
        messageString += ('\nUsing T-1 Merlin Curves located in \n%s.' % self.TMinusOnePath if self.TMinusOnePath else '')
        messageString += ('\nUsing PNGS to generate PDF or email, located in \n%s.' % self.PNGInputPath if self.PNGInputPath else '')
        messageString += ('\nPDF will be output to\n%s.' % self.PDFPath if self.PDFPath else '')

        return messageString
            
    ##########################################################
    ## Class Properties:
    ##########################################################
    @property
    def ConfigFilePath(self):
        " Return overwrite path to configuration file. "
        return self.__ConfigFilePath
    @property
    def NoEmailMode(self):
        " Indicate whether application will generate the final PNG email. "
        return self.__NoEmailMode
    @property
    def NoPDFMode(self):
        " Return whether application will generate PDF. "
        return self.__NoPDFMode
    @property
    def NoLogFileMode(self):
        " Indicate whether application will generate a log file. "
        return self.__NoLogFileMode
    @property
    def PNGInputPath(self):
        " Return PNG override input folder path. "
        return self.__PNGInputPath
    @property
    def PNGOutputPath(self):
        " Return PNG override output folder path. "
        return self.__PNGOutputPath
    @property
    def PDFPath(self):
        " Return the overridden PDF path."
        return self.__PDFPath
    @property
    def RunTime(self):
        " Indicate application run time. "
        return self.__RunTime
    @property
    def TestImagePath(self):
        " Return path to generated test image."
        return self.__TestImagePath
    @property
    def TMinusOne(self):
        " Return the T-1 date. "
        return self.__TMinusOne
    @property
    def TMinusOnePath(self):
        " Return path to the T-1 Merlin discount factor files. "
        return self.__TMinusOnePath
    @property
    def TMinusOnePath(self):
        " Return override path to T-1 Merlin discount factors. "
        return self.__TMinusOnePath
    @property
    def TPath(self):
        " Return override path to the T Merlin discount factors."
        return self.__TPath
    @property
    def UATMode(self):
        " Indicate if application is in UAT mode. "
        return self.__UATMode
    @property
    def ValueDate(self):
        " Return application's value date. "
        return self.__ValueDate

    ##########################################################
    ## Mutators:
    ##########################################################
    @ConfigFilePath.setter
    def ConfigFilePath(self, configFilePath):
        """
        * Set the configuration file override path.
        Inputs:
        * configFilePath: Expecting a string path with file extension 'csv'. If not satisfied or None then will set to default variable.
        """
        if isinstance(configFilePath, str) and self.ExtractExtension(configFilePath) == '.csv':
            configFilePath = self.FixPath(configFilePath)
            if not self.CheckPath(configFilePath):
                raise ValueError('Path does not exist.')
            self.__ConfigFilePath = configFilePath
        elif configFilePath is None:
            # Set to default value if not a csv file or none was passed:
            self.__ConfigFilePath = ''
        else:
            raise ValueError('Must be a string csv file path or None.')
    
    @NoEmailMode.setter
    def NoEmailMode(self, noEmailMode):
        """
        * Validate and set NoEmail mode, throw exception if failed. 
        Inputs:
        * noEmailMode: Expecting a boolean, None or string that can be converted to boolean.
        """
        if noEmailMode is None:
            # Set to default:
            self.__NoEmailMode = False
        elif isinstance(noEmailMode, bool):
            self.__NoEmailMode = noEmailMode
        elif isinstance(noEmailMode, str):
            self.__NoEmailMode = StrToBool(noEmailMode)
        else:
            raise ValueError('Must be string or boolean.')

    @NoLogFileMode.setter
    def NoLogFileMode(self, logFile):
        """
        * Validate and set LogFile mode, throw exception if failed. 
        Inputs:
        * logFile: Expecting a boolean, None or string that can be converted to boolean.
        """
        if logFile is None:
            # Set to default:
            self.__NoLogFileMode = False
        elif isinstance(logFile, bool):
            self.__NoLogFileMode = logFile
        elif isinstance(logFile, str):
            self.__NoLogFileMode = StrToBool(logFile)
        else:
            raise ValueError('Must be string or boolean.')

    @NoPDFMode.setter
    def NoPDFMode(self, nopdf):
        """
        * Validate and set NoPDFMode.
        Inputs:
        * nopdf: Expecting a boolean, None or string that can be converted to boolean.
        """
        if nopdf is None:
            # Set to default:
            self.__NoPDFMode = False
        elif isinstance(nopdf, bool):
            self.__NoPDFMode = nopdf
        elif isinstance(nopdf, str):
            self.__NoPDFMode = StrToBool(nopdf)
        else:
            raise ValueError('Must be a string or boolean.')
    
    @PDFPath.setter
    def PDFPath(self, pdfOutput):
        """
        * Validate and set the pdf override path.
        Inputs:
        * pdfOutput: Expecting a string path that can contain signature symbols, else if None is passed then
        will get set to default string.
        """
        if pdfOutput is None or self.NoPDFMode:
            # Eliminate the PDF output path if application is in NoPDFMode:
            self.__PDFPath = ''
        elif isinstance(pdfOutput, str):
            # If filename was included and not a pdf then raise exception:
            if '.' in pdfOutput and '.pdf' not in pdfOutput:
                raise ValueError('File must be a PDF.')
            pdfOutput = self.AppendHyphenIfNecessary(pdfOutput)
            pdfOutput = self.FixPath(pdfOutput)
            # Use default PDF signature if filename not provided in path:
            pdfOutput += ('{MM}{DD}{YY} {RunTime} Merlin Graphs.pdf' if '.pdf' not in pdfOutput else '')
            self.__PDFPath = pdfOutput
        else:
            raise ValueError('Must be a string or None.')

        # Cancel conflicting settings if a valid pdf path was provided:
        if self.PDFPath:
            self.NoPDFMode = False

    @PNGInputPath.setter
    def PNGInputPath(self, path):
        """
        * Validate and set the png input override path.
        Inputs:
        * path: Expecting None or a string. If None then property will be set to
        blank string.
        """
        if path is None:
            # Set to default:
            self.__PNGInputPath = ''
        elif isinstance(path, str):
            path = self.AppendHyphenIfNecessary(path)
            path = self.ExtractFolderName(path)
            path = self.FixPath(path)
            if not self.CheckPath(path):
                raise ValueError('Path does not exist.')
            self.__PNGInputPath = path
        else:
            raise ValueError('Must be a string or None.')

    @PNGOutputPath.setter
    def PNGOutputPath(self, pdfOutput):
        """
        * Validate and set the png output override pdfOutput.
        Inputs:
        * pdfOutput: Expecting None or a string path that can contain signature symbols. If None then property will be set 
        to a blank string.
        """
        if pdfOutput is None:
            # Set to default:
            self.__PNGOutputPath = ''
        elif isinstance(pdfOutput, str):
            # If filename signature was included and not a png then raise exception:
            if '.' in pdfOutput and '.png' not in pdfOutput:
                raise ValueError('Must use .png extension.')
            pdfOutput = self.AppendHyphenIfNecessary(pdfOutput)
            pdfOutput = self.FixPath(pdfOutput)
            self.__PNGOutputPath = pdfOutput + ('{YYYY}-{MM}-{DD} MerlinCurveGraph-{PlotName}-{RunTime}.png' if '.png' not in pdfOutput else '')
        else:
            raise ValueError('Must be a string or None.')

    @RunTime.setter
    def RunTime(self, runTime):
        """
        * Validate and set RunTime, throw exception if failed. 
        Inputs:
        * runTime: Expecting string, one of AM/PM/CAPULA.
        """
        runTime = (runTime if not isinstance(runTime, str) else runTime.upper())
        if not isinstance(runTime, str):
            raise ValueError('Must be a string.')
        elif runTime not in ('AM', 'PM', 'CAPULA'):
            raise ValueError('Must be one of {AM/PM/CAPULA}.')
        self.__RunTime = runTime

    @TMinusOne.setter
    def TMinusOne(self, t1Override):
        """
        * Validate and set T-1 date, throw exception if failed. 
        Inputs:
        * t1Override: Expecting a datetime or date object, convertible string or None.
        """
        if isinstance(t1Override, datetime.datetime):
            self.__TMinusOne  = t1Override.date()
        elif isinstance(t1Override, datetime.date) or t1Override is None:
            self.__TMinusOne  = t1Override
        elif isinstance(t1Override, str):
            if self.__StringIsDate(t1Override):
                self.__TMinusOne = datetime.datetime.strptime(t1Override, "%m/%d/%Y").date()
            else:
                raise ValueError('Could not be converted to datetime.')
        else:
            raise ValueError('Must be a datetime object or convertible string.')
        
        # Ensure that T-1 is before T and is a weekday:
        if not self.__TMinusOne is None and self.__TMinusOne.isoweekday() >= 6:
            raise ValueError('Must be week day.')
        elif self.__ValueDate and self.__TMinusOne and self.__TMinusOne > self.__ValueDate:
            raise ValueError('Must be before ValueDate.')

    @TMinusOnePath.setter
    def TMinusOnePath(self, tMinusOnePath):
        """
        * Validate and set override path to T-1 Merlin discount factors.  
        Input:
        * tMinusOnePath: Expecting a string folder path that exists, filepath with signature whose folder exists, or None. If not satisfied
        then exception will throw.
        """
        if isinstance(tMinusOnePath, str):
            if '.' in tMinusOnePath and '.txt' not in tMinusOnePath:
                raise ValueError('Path signature must use .txt extension.')
            elif '.' in tMinusOnePath  and '{' not in tMinusOnePath and '}' not in tMinusOnePath:
                raise ValueError('Must use valid signature if providing file name.')
            elif not self.CheckPath(self.ExtractFolderName(tMinusOnePath)):
                raise ValueError('Path does not exist.')
            tMinusOnePath = self.AppendHyphenIfNecessary(tMinusOnePath)
            tMinusOnePath = self.FixPath(tMinusOnePath)
            # Use default signature if not specified at command line:
            tMinusOnePath += ('{CurveName}.txt' if '.txt' not in tMinusOnePath else '')
            self.__TMinusOnePath = tMinusOnePath
        elif tMinusOnePath is None:
            # Set to default value:
            self.__TMinusOnePath = ''
        else:
            raise ValueError('Must be string path to folder that exists, filepath with signature whose folder exists, or None.')

    @TPath.setter
    def TPath(self, tPath):
        """
        * Validate and set override path to T Merlin discount factors.  
        Input:
        * tPath: Expecting a string folder path that exists, filepath with signature whose folder exists, or None. If not satisfied
        then exception will throw.
        """
        if isinstance(tPath, str):
            if '.' in tPath and '.txt' not in tPath:
                raise ValueError('Path must use .txt extension.')
            elif '.' in tPath and '{' not in tPath and '}' not in tPath:
                raise ValueError('Must use valid signature if providing file name.')
            elif not self.CheckPath(self.ExtractFolderName(tPath)):
                raise ValueError('Path does not exist.')
            tPath = self.AppendHyphenIfNecessary(tPath)
            tPath = self.FixPath(tPath)
            # Use default signature if not specified at command line:
            tPath += ('{CurveName}.txt' if '.txt' not in tPath else '')
            self.__TPath = tPath
        elif tPath is None:
            # Set to default value:
            self.__TPath = ''
        else:
            raise ValueError('Must be string path to folder that exists, filepath with signature whose folder exists, or None')

    @TestImagePath.setter
    def TestImagePath(self, testPath):
        """
        * Validate and set the path to output the test image.
        Input:
        * testPath: Expecting a string folder path that exists or None. If not satisfied
        then exception will throw.
        """
        if isinstance(testPath, str):
            # If filename was included and not a png then raise exception:
            if '.' in testPath and '.png' not in testPath:
                raise ValueError('Signature must use .png extension.')
            testPath = self.AppendHyphenIfNecessary(testPath)
            testPath = self.FixPath(testPath)
            # Use default image name if not provided:
            testPath = testPath + ('{YYYY}-{MM}-{DD} MerlinCurveGraph-{PlotName}-{RunTime}.png' if '.png' not in testPath else '')
            self.__TestImagePath = testPath
            # Set the application mode to skip all steps except for generating the test image:
            self.NoEmailMode = True
            self.NoPDFMode = True
        elif testPath is None:
            self.__TestImagePath = ''
        else:
            raise ValueError('Must be a string path to a folder or None.')
        
    @UATMode.setter
    def UATMode(self, uat):
        """
        * Validate and set UATMode, throw exception if failed. 
        Input:
        * uat: Expecting a boolean value or string convertible to boolean.
        """
        if uat is None:
            # Set to default:
            self.__UATMode = False
        elif isinstance(uat, str):
            self.__UATMode = StrToBool(uat)
        elif isinstance(uat, bool):
            self.__UATMode = uat
        else:
            raise ValueError('Must be boolean or string convertible to boolean.')
        # If application is in UATMode then negate all of the provided overwrite input and output paths:
        """
        if self.__UATMode:
            self.ConfigFilePath = None
            self.TPath = None
            self.TMinusOnePath = None
            self.PDFPath = None
            self.PNGInputPath = None
            self.PNGOutputPath = None
        """

    @ValueDate.setter
    def ValueDate(self, valueDate):
        """
        * Validate and set ValueDate, throw exception if failed.
        Inputs:
        * valueDate: Expecting datetime or date object or convertible string.
        """
        if isinstance(valueDate, datetime.datetime):
            self.__ValueDate = valueDate.date()
        elif isinstance(valueDate, datetime.date):
            self.__ValueDate = valueDate
        elif isinstance(valueDate, str) and self.__StringIsDate(valueDate):
            self.__ValueDate = datetime.datetime.strptime(valueDate, "%m/%d/%Y").date()
        else:
            raise ValueError('Must be a datetime or date object or convertible string.')

        # Ensure that passed value date is a week day, is later than T-1 date. Set T-1 date if hasn't been set.
        if self.__ValueDate.isoweekday() >= 6:
            raise ValueError('Must be week day.')
        elif not self.TMinusOne:
            # Only set the T-1 date if not overwritten:
            self.TMinusOne = GetTMinusOne(self.ValueDate)
        elif self.__ValueDate and self.__TMinusOne > self.__ValueDate:
            raise ValueError('T-1 must be before ValueDate.')

    ##########################################################
    ## Private Helpers:
    ##########################################################
    def __StringIsDate(self, dateString):
        """
        * Return true if passed string is a date.
        Input:
        * dateString: String that could possibly represent a date.
        Output:
        * Return true if passed date can be converted to a datetime object.
        """
        try:
            datetime.datetime.strptime(dateString, "%m/%d/%Y").date()
            return True
        except:
            return False

    def __StrToDate(self, dateString):
        """
        * Return string converted to date object if passed string is a date.
        Input:
        * dateString: String that could possibly represent a date.
        Output:
        * Return converted date object.
        """
        if not self.__StringIsDate(dateString):
            raise argparse.ArgumentTypeError('"{0}" not a valid date.'.format(dateString))

        return datetime.datetime.strptime(dateString, "%m/%d/%Y").date()