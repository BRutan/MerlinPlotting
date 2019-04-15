##############################################################################
## CustomAxisItems.py
##############################################################################
## Description:
## * Classes (derived from AxisItem) used in setting axis presentation for plots.

import datetime
import decimal
import numbers
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import sys

__all__ = ['PercentAxis', 'TimeAxis']

class PercentAxis(pg.AxisItem):
    " Converts floating point data to display as percentages with 2 decimal places. "
    # Use static variable to set the number of ticks to display:
    numTicks = 8
    __formatStringBase = "{0:.%df}%%"
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, *args, **kwargs):
        """ Overloaded constructor.
        " Optional Inputs:
        " * DecimalPoints: Specify the number of decimal points in string. """
        # Use superclass instantiation depending upon python version number.
        if sys.version_info[0] > 2:
            super().__init__(*args, **kwargs)
        else:
            super(PercentAxis, self).__init__(*args, **kwargs)

        decimalPoints = kwargs.get("DecimalPoints", 2)
        self.DecimalPoints = decimalPoints

    ##########################################################
    ## Properties:
    ##########################################################
    @property
    def DecimalPoints(self):
        """
        * Return number of decimal points used in displaying %ages on this axis.
        """
        return self.__decimalPoints
    
    @property
    def FormatString(self):
        """
        * Return the format string.
        """
        return self.__formatString
    
    @DecimalPoints.setter
    def DecimalPoints(self, numDecimals):
        """
        * Set the number of decimal points to use in displaying the %ages on this axis, and update the format string.
        Inputs:
        * numDecimals: Expecting an integer. Will get set to 2 by default.
        """
        if not isinstance(numDecimals, int):
            self.__decimalPoints = 2
        elif numDecimals > 5:
            self.__decimalPoints = 2;
        else:
            self.__decimalPoints = numDecimals

        self.__formatString = PercentAxis.__formatStringBase  % self.DecimalPoints

    ##########################################################
    ## Class Methods:
    ##########################################################
    def TickString(self, value):
        """
        * Return formatted string to present on axis.
        """
        return self.__formatString.format(float(value) * 100)

    def tickStrings(self, values, scale, spacing):
        """
        * Format all datapoints to use percentage with specified # digits (2 by default).
        """
        # Use 1 decimal point if any 2 digit percentages appear in graph:
        if len([value for value in values if value * 10 >= 1]) > 0:
            self.DecimalPoints = 1
            
        return [self.TickString(value) for value in values]

class TimeAxis(pg.AxisItem):
    " Object formats axis to display dates as strings. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, *args, **kwargs):
        " Overloaded constructor. "
        # Use superclass instantiation depending upon python version.
        if sys.version_info[0] > 2:
            super().__init__(*args, **kwargs)
        else:
            super(TimeAxis, self).__init__(*args, **kwargs)
         
    ##########################################################
    ## Class Methods:
    ##########################################################
    def tickStrings(self, values, scale, spacing):
        """
        * Format all datapoints using "mm/dd/yyyy" date representation.
        """
        return [datetime.datetime.strftime(self.ExcelSerialToDatetime(value),'%m/%d/%Y') for value in values]

    def SkiptickValues(self, minVal, maxVal, size):
        """
        * Output fixed number of dates for each graph:
        """
        minVal, maxVal = sorted((minVal, maxVal))
            
        ticks = []
        tickLevels = self.tickSpacing(minVal, maxVal, size)

        allValues = np.array([])
        for i in range(len(tickLevels)):
            if i == len(tickLevels) - 1:
                step = float(maxVal - minVal) / float(12)
                currVal = minVal
                values = []
                while currVal <= maxVal:
                    values.append(int(currVal))
                    currVal += step
            else:
                spacing, offset = tickLevels[i]
            
                ## determine starting tick
                start = (np.ceil((minVal-offset) / spacing) * spacing) + offset
            
                ## determine number of ticks
                num = int((maxVal-start) / spacing) + 1
                values = (np.arange(num) * spacing + start) / self.scale
                ## remove any ticks that were present in higher levels
                ## we assume here that if the difference between a tick value and a previously seen tick value
                ## is less than spacing/100, then they are 'equal' and we can ignore the new tick.
                values = list(filter(lambda x: all(np.abs(allValues-x) > spacing*0.01), values) )
                allValues = np.concatenate([allValues, values])
            ticks.append((spacing/self.scale, values))
            
        if self.logMode:
            return self.logTickValues(minVal, maxVal, size, ticks)
    
        return ticks
        
    def ExcelSerialToDatetime(self, xldate):
        """
        * Convert Excel serial date to a datetime object.
        """
        temp = datetime.datetime(1900, 1, 1)
        delta = datetime.timedelta(days=int(xldate))
    
        return temp + delta
"""
class TimeAxis_3D(gl.GLAxisItem):
    " Object formats axis to display dates as strings. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, *args, **kwargs):
        " Overloaded constructor. "
        # Use superclass instantiation depending upon python version number.
        # Rotate the labels 90 degrees.
        if sys.version_info[0] > 2:
            super().__init__(*args, **kwargs)
        else:
            super(TimeAxis_3D, self).__init__(*args, **kwargs)
            
        self.rotate(90, 1, 0, 0)

    ##########################################################
    ## Class Methods:
    ##########################################################
    def tickStrings(self, values, scale, spacing):

        * Format all datapoints using "mm/dd/yyyy" date representation.

        return [datetime.datetime.strftime(self.ExcelSerialToDatetime(value),'%m/%d/%Y') for value in values]

    def ExcelSerialToDatetime(self, xldate):

        Convert Excel serial date to a datetime object.

        temp = datetime.datetime(1900, 1, 1)
        delta = datetime.timedelta(days=int(xldate))
    
        return temp + delta
"""