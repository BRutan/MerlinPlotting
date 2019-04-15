##############################################################################
## PlottingConfigFile.py
##############################################################################
## Description:
## * Stores and handles all data in "Curve Plotting Configuration.csv" file. 
##  Note that path is hard coded to be contained in a local 
##  \\Configs\\{UAT/Production}\\Curve Plotting Configuration.csv folder.

import csv
from DirectoryTypes.FileType import FileType
from DirectoryTypes.FileRow import FileRow
from DirectoryTypes.PathSubscriber import PathSubscriber
import Exceptions.Fatal as Fatals
import sortedcontainers
import sys

__all__ = [ 'CurveConfig', 'PlottingConfigFile' ]

class PlottingConfigFile(FileType):
    " PlottingConfigFile: Stores and handles all plot configurations stored in Curve Plotting Configuration.csv file. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, UATMode):
        """
        * Overloaded constructor that sets object path to passed Path object.
        Inputs:
        * UATMode: Expecting a boolean value. The file will use production paths if is not a boolean or is True.
        """
        UATMode = (False if not isinstance(UATMode, bool) else UATMode)
        path = FileType.ConvertSignature("{LocalPath}\\Configs\\{UAT/Prod}\\Curve Plotting Configuration.csv", UAT = UATMode)
        name = FileType.ExtractFileName(path)
        self.__Plots = None
        self.__InsertionTracker = None
        if sys.version_info[0] > 2:
            super().__init__(path, name)
        else:
            super(PlottingConfigFile, self).__init__(path, name)
        
    ##########################################################
    ## Accessors:
    ##########################################################
    @property
    def ConfiguredPlots(self):
        """
        * Return dictionary containing configured plots in current order in plots container.
        """
        return self.__Plots

    @property
    def PlotsInOrder(self):
        """
        * Return list of plot titles in the order they appear in the configuration file.
        """
        return self.__InsertionTracker

    def GetFirstCurveNameRow(self, curveName):
        """
        * Return first instance of CurveConfig() row that matches given curveName (primary key of row).
        Inputs:
        * curveName: Name of curve desired.
        """
        for rowGroup in self.__Plots.items():
            if curveName in rowGroup:
                return rowGroup[curveName]
        # Return null object if could not find:
        return None

    ##########################################################
    ## Mutators:
    ##########################################################
    def GetContents(self):
        """
        * Pull in all contents from the configuration file at stored path.
        """
        # Attempt to open csv at stored path:
        if not FileType.CheckPath(self.Path):
            raise Fatals.ConfigFilesMissing(callingFunc = 'PlottingConfigFile::GetContents()', fileName = self.Name, filePath = self.Path)
        # Reset the plot container and insertion order tracker:
        self.__Plots = {}
        self.__InsertionTracker = []
        ##############################
        # Pull contents from file:
        ##############################
        atHeader = True
        try:
            with open(self.Path, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if not atHeader:
                        # Add new entry for plot if not already in stored map:
                        plotTitle = row[0].strip()
                        if plotTitle not in self.__Plots.keys():
                            self.__Plots[plotTitle] = {}
                            self.__InsertionTracker.append(plotTitle)
                        # Create new row for mapper:
                        newRow = CurveConfig([col.strip() for col in row])
                        # Append new row to mapper:
                        self.__Plots[plotTitle][newRow.Curve] = newRow
                    atHeader = False
        except Exception as err:
            raise Fatals.ConfigFilesMissing(callingFunc = 'PlottingConfigFile::GetContents()', fileName = self.Name, filePath = self.Path, specific = err.message)

class CurveConfig(FileRow):
    " Simple object to hold all attributes of curve configurations ( { Curve Name, Plot T-1, RunTime, FwdRateConv } ) "
    ##########################################################
    ## Constructors/Magic Methods:
    ##########################################################
    def __init__(self, *args, **kwargs):
        """
        * Overloaded constructor. Instantiate row containing data pertaining to curve name property (primary key) within a plot.
        Inputs:
        * PlotTitle: Name of overall plot this curve is associated to. Serves as primary key in container.
        * Curve: string name of Merlin Curve for this plotting configuration.
        * PlotT1: boolean indicating whether to plot T-1 version of this curve to graph.
        * RunTime: Batch time, expecting to be one of {AM, PM, CAPULA}.
        * FwdRateConv: Numeric value indicating the days in period to calculate forward rate.
        """
        # Use positional arguments if specified, else use the dictionary arguments:
        if args:
            args = (args[0] if isinstance(args[0], list) else args)
            self.PlotTitle = args[0]
            self.Curve = args[1]
            self.PlotT1  = args[2]
            self.RunTime = args[3]
            self.FwdRateConv = args[4]
        else:
            self.PlotTitle = kwargs.get('PlotTitle', None)
            self.Curve = kwargs.get('Curve', None)
            self.PlotT1 = kwargs.get('PlotT1', None)
            self.RunTime = kwargs.get('RunTime', None)
            self.FwdRateConv = kwargs.get('RunTime', None)
        # Allow this object to be iterable:
        self.__CurrIterIndex = 0
    def __iter__(self):
        """
        * Enable iteration on this class.
        """
        return self
    def next(self):
        """
        * Get next iterator for this object.
        """
        if self.__CurrIterIndex > 6:
            # Reset the iterator count:
            self.__CurrIterIndex = 0
            raise StopIteration
        else:
            self.__CurrIterIndex += 1
            # Return appropriate value:
            self.Get(self.__CurrIterIndex - 1)

    ##########################################################
    ## Accessors:
    ##########################################################
    def Get(self, index):
        """
        * Return value at index.
        Inputs:
        * index: Index requested (in [0, 4]).
        """
        if index == 0:
            return self.PlotTitle
        elif index == 1:
            return self.Curve
        elif index == 2:
            return self.PlotT1
        elif index == 3:
            return self.RunTime
        elif index == 4:
            return self.FwdRateConv
        else:
            raise IndexError('Index ' + index + ' is out of bounds.')

    @property
    def Curve(self):
        """
        * Return the name of the curve.
        Output:
        * Curve: string name of curve.
        """ 
        return self.__Curve

    @property
    def FwdRateConv(self):
        """
        * Return the forward rate convention.
        Output:
        * FwdRateConv: Floating point number.
        """
        return self.__FwdRateConv

    @property
    def PlotT1(self):
        """
        * Return the include T-1 option status.
        Output:
        * PlotT1: boolean value. 
        """
        return self.__PlotT1

    @property
    def PlotTitle(self):
        """
        * Get the title of the plot associated with this curve (serves as primary key for container).
        """
        return self.__PlotTitle

    @property
    def RunTime(self):
        """
        * Return the batch time when this curve is generated.
        Output:
        * RunTime: string, one of {AM, PM, CAPULA}
        """
        return self.__RunTime

    ##########################################################
    ## Mutators:
    ##########################################################
    def Set(self, index, value):
        """
        * Set value at index.
        Inputs:
        * index: Index requested (in [0, 4]).
        * value: Value to set attribute to.
        """
        if index == 0:
            self.PlotTitle = value
        elif index == 1:
            self.Curve = value
        elif index == 2:
            self.PlotT1 = value
        elif index == 3:
            self.RunTime = value
        elif index == 4:
            self.FwdRateConv = value
        else:
            raise IndexError('Index ' + index + ' is out of bounds.')

    @Curve.setter
    def Curve(self, value):
        """
        * Set the name of the curve.
        Inputs:
        * value: Expecting string or None (will assign default).
        """ 
        if isinstance(value, str):
            self.__Curve = value
        elif value is None:
            # Set to default value:
            self.__Curve = ''
        else:
            raise ValueError('Curve must be a string or None.')

    @FwdRateConv.setter
    def FwdRateConv(self, value):
        """
        * Set the forward rate convention.
        Output:
        * FwdRateConv: Floating point number.
        """
        if type(value) in [float, int]:
            self.__FwdRateConv = float(value)
        elif isinstance(value, str) and value.isdigit():
            self.__FwdRateConv = float(value)
        elif value is None:
            self.__FwdRateConv = 0.0
        else:
            raise ValueError('FwdRateConv must be numeric type, numeric string or None.')

    @PlotT1.setter
    def PlotT1(self, value):
        """
        * Determine if want to include T-1 version of curve in graph.
        Inputs:
        * value: Expecting string that can be converted to a boolean, boolean or None (will assign default).
        """
        if isinstance(value, str):
            # Attempt to convert string to boolean:
            self.__PlotT1 = FileRow.StrToBool(value)
        elif isinstance(value, bool):
            self.__PlotT1 = value
        elif value is None:
            # Set to default value:
            self.__PlotT1 = False
        else:
            raise ValueError('PlotT1 must be string ("TRUE"/"FALSE"), boolean or None.')

    @PlotTitle.setter
    def PlotTitle(self, value):
        """
        * Set the title of the plot associated with this curve (serves as primary key for container).
        Inputs:
        * value: string plot title. If None is passed then gets set to default string.
        """
        if value is None:
            self.__PlotTitle = ''
        elif isinstance(value, str):
            self.__PlotTitle = value
        else:
            raise ValueError('PlotTitle must be string or None.')

    @RunTime.setter
    def RunTime(self, value):
        """
        * Set the batch time when this curve is generated.
        Outputs:
        * RunTime: string, one of {AM, PM, CAPULA}
        """
        if value is None:
            # Set to default value for now:
            self.__RunTime = ''
        elif isinstance(value, str):
            if value not in ['AM','PM','CAPULA']:
                raise ValueError('RunTime must be one of {AM, PM, CAPULA}.')
            else:
                self.__RunTime = value
        else:
            raise ValueError('RunTime must be one of {AM, PM, CAPULA} or None.')
