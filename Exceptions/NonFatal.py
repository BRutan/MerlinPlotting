##############################################################################
## NonFatal.py
##############################################################################
## Description:
## * Contains all non-fatal exceptions that will not trigger application
## close when raised, but will be output to log file and stdout.
## All non-fatal exceptions will be handled by ExceptionAggregator class, since the application 
## can have multiple non-fatal errors:

from abc import ABCMeta, abstractmethod
from datetime import datetime
import Exceptions.MerlinPlottingExcept as base
import Exceptions.ExceptionContainerType as Container
import DirectoryTypes.PathType as PathType
import sys
from sortedcontainers import SortedList
from Misc.Utilities import StringIsDate

__all__ = [ 'FailedToGeneratePNGS', 'FailedToGeneratePDF', 'FailedToOutputPNGS', 'MerlinCurvesMissing', 'NoPlotsLoaded', 'OutlookFailed', 'NonFatal' ]

########################################################################################################
# Base Classes:
########################################################################################################
class NonFatal(base.MerlinPlottingExcept):
    " Abstract base class for non-fatal exceptions, that will be printed and output to log file on application exit."
    __metaclass__ = ABCMeta
    ##########################################################
    ## Constructors:
    ##########################################################  
    def __init__(self, callingFunc, specific = '', timestamp = datetime.now()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp)
        else:
            super(NonFatal, self).__init__(callingFunc, specific, timestamp)

########################################################################################################
# Derived Classes:
########################################################################################################
class FailedToGeneratePNGS(Container.ExceptionContainerType, NonFatal):
    " Exception thrown when particular PNG plot failed to be generated. "
    __Concise = 'Failed to generate %d PNGs.'
    __Granular = 'Failed to generate the following PNG charts: \n{%s}'
    ##########################################################
    ## Constructors:
    ##########################################################  
    def __init__(self, callingFunc, plotTitle = '', specific = '', timestamp = datetime.now(), targetList = SortedList()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp, targetList)
        else:
            super(FailedToGeneratePNGS, self).__init__(callingFunc, specific, timestamp, targetList)
        
        self.Add(plotTitle)

    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            return FailedToGeneratePNGS.__Granular % (super() if sys.version_info[0] > 2 else super(FailedToGeneratePNGS, self)).Message() 
        else:
            return FailedToGeneratePNGS.__Concise % self.ErrorCount()

    ##########################################################
    ## Mutators:
    ##########################################################    
    def Merge(self, failedToGenerate):
        """
        * Merge the passed container/FailedToGeneratePNGS object.
        Inputs:
        * failedToGenerate: Expecting a FailedToGeneratePNGS exception object, list, SortedList or None.
        """
        # Below method will throw exception if type is incorrect:
        self.TypesMatch(failedToGenerate, FailedToGeneratePNGS)
        # Merge the passed container with base class container:
        (super() if sys.version_info[0] > 2 else super(FailedToGeneratePNGS, self)).Merge(failedToGenerate)

class FailedToGeneratePDF(NonFatal, PathType.PathType):
    " Exception thrown when PDF fails to generate. "
    __Concise = 'Failed to generate PDF.'
    __Granular = 'Failed to generate PDF at path: \n{%s}'
    ##########################################################
    ## Constructors:
    ##########################################################    
    def __init__(self, pdfPath, callingFunc, specific = '', timestamp = datetime.now()):
        """
        * Overloaded Constructor.
        """        
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp)
        else:
            super(FailedToGeneratePDF, self).__init__(callingFunc, specific, timestamp)

        # Detail the PDF path that could not be output to within this exception:
        self.Path = pdfPath

    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            return FailedToGeneratePDF.__Granular % self.Path
        else:
            return FailedToGeneratePDF.__Concise

class MerlinCurvesMissing(Container.ExceptionContainerType, NonFatal):
    " Exception contains list of Merlin Curves that could not be found in production locations. "
    __Concise = '%d Merlin Curves could not be found in production locations. '
    __Granular = 'The following Merlin Curves are missing from production: { %s }'
    ##########################################################
    ## Constructors:
    ##########################################################  
    def __init__(self, callingFunc, missingCurve = '', specific = '', timestamp = datetime.now(), targetList = SortedList()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp, targetList)
        else:
            super(MerlinCurvesMissing, self).__init__(callingFunc, specific, timestamp, targetList)
        
        self.Add(missingCurve)

    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            return MerlinCurvesMissing.__Granular % (super() if sys.version_info[0] > 2 else super(MerlinCurvesMissing, self)).Message()
        else:
            return MerlinCurvesMissing.__Concise % self.ErrorCount()

    ##########################################################
    ## Mutators:
    ##########################################################    
    def Merge(self, merlinCurvesMissing):
        """
        * Merge the passed container/FailedToGeneratePNGS object.
        Inputs:
        * merlinCurvesMissing: Expecting a MerlinCurvesMissing exception object, list, SortedList or None.
        """
        # Below method will throw exception if type is incorrect:
        self.TypesMatch(merlinCurvesMissing, MerlinCurvesMissing)
        # Merge the passed container with base class container:
        (super() if sys.version_info[0] > 2 else super(MerlinCurvesMissing, self)).Merge(merlinCurvesMissing)

class NoPlotsLoaded(Container.ExceptionContainerType, NonFatal):
    " Exception thrown when no Merlin Curves were loaded into a particular ForwardRatePlot object. "
    __Concise = '%d plots had no Merlin Curves added to configuration.'
    __Granular = 'The following plots had no Merlin Curves in the configuration: \n{%s}' 
    ##########################################################
    ## Constructors:
    ##########################################################  
    def __init__(self, callingFunc, plotTitle = '', specific = '', timestamp = datetime.now(), targetList = SortedList()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp, targetList)
        else:
            super(NoPlotsLoaded, self).__init__(callingFunc, specific, timestamp, targetList)
    
        self.Add(plotTitle)
        
    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            return NoPlotsLoaded.__Granular % (super() if sys.version_info[0] > 2 else super(NoPlotsLoaded, self)).Message()
        else:
            return NoPlotsLoaded.__Concise % self.ErrorCount()
    
    ##########################################################
    ## Mutators:
    ##########################################################    
    def Merge(self, noPlotsLoaded):
        """
        * Merge the passed NoPlotsLoaded object or container type with this object:
        Inputs:
        * noPlotsLoaded: Expecting a NoPlotsLoaded exception object, list, SortedList or None.
        """
        # Raise exception if incorrect type passed:
        self.TypesMatch(noPlotsLoaded, NoPlotsLoaded)
        # Merge the passed container with base class container:
        (super() if sys.version_info[0] > 2 else super(NoPlotsLoaded, self)).Merge(noPlotsLoaded)
                

class OutlookFailed(NonFatal):
    " Exception thrown when outlook message failed to generate. "
    __Concise = 'The Outlook email failed to generate.'
    __Granular = 'Outlook error: %s'
    ##########################################################
    ## Constructors:
    ##########################################################    
    def __init__(self, callingFunc, specific = '', timestamp = datetime.now()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp)
        else:
            super(OutlookFailed, self).__init__(callingFunc, specific, timestamp)

    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            return OutlookFailed.__Granular % self.SpecificMessage
        else:
            return OutlookFailed.__Concise

class LogFileFailed(NonFatal, PathType.PathType):
    " Exception thrown when LogFile could not be printed. "
    __Concise = 'The LogFile could not be generated. '
    __Granular = 'LogFile could not be generated at \n%s'
    ##########################################################
    ## Constructors:
    ##########################################################    
    def __init__(self, callingFunc, logPath = '', specific = '', timestamp = datetime.now()):
        if sys.version_info[0] > 2:
            super().__init__(callingFunc, specific, timestamp)
        else:
            super(LogFileFailed, self).__init__(callingFunc, specific, timestamp)

        self.Path = logPath

    ##########################################################
    ## Class Methods:
    ##########################################################    
    def Message(self, granular = False):
        """
        * Return the granular or concise message.
        """
        if granular:
            # Add default granular message:
            granular = LogFileFailed.__Granular % (self.Path)
            # Add information regarding specific reason why could not be output if available:
            if self.SpecificMessage:
                granular += '\nreason: %s' % self.SpecificMessage

            return granular
        else:
            return LogFileFailed.__Concise