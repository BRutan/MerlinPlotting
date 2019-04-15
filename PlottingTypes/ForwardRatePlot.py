##############################################################################
## ForwardRatePlot.py
##############################################################################
## Description:
## * Class pulls in data, calculates forward rates and loads into plot for single 
## curve.

from __future__ import division
from collections import OrderedDict
import csv
import datetime 
import ConfigurationTypes.PlottingConfigFile as PlotConfig
from DirectoryTypes.FileType import FileType
import Exceptions.Fatal as Fatals
import Exceptions.NonFatal as NonFatals
import FixedImageExporter
import Misc.Utilities as util
import pyqtgraph as pg
import pyqtgraph.exporters
from pyqtgraph.Qt import QtCore, QtGui
from PlottingTypes.CustomAxisItems import PercentAxis, TimeAxis
from PlottingTypes.Plot import Plot
from random import randint
import os

__all__ = ['ForwardRatePlot']

# Set the default background for all charts to be white:
pyqtgraph.setConfigOption('background','w')

class ForwardRatePlot(FileType, Plot):
    " Object represents pyqtgraph generated PNG graph with one or more Merlin Curves plotted, using curve configurations listed in the 'Curve Configurations.xlsx' file."
    ##########################################################
    ## Static Variables:
    ##########################################################
    # https://groups.google.com/forum/#!topic/pyqtgraph/X7fL1KfXalY
    # Container for all possible color schemes for plots, which will be randomly set at object initialization: 
    __plotColors = [['#7fff00','#ff0000','#0000ff','#ffd700','#9400d3'], ['#9400d3','#ff8c00','#7fff00','#2f5f00','#00BFFF'], ['#008080','#ff4500','#2f5f00','#9400d3','#00BFFF']]
    # Initiate the QtGUI application as static variable:
    __app = QtGui.QApplication([])
    # Use same font for each axis: QtGui.QFont.Normal
    __axisFont = QtGui.QFont("Times New Roman", 7, 100, False)
    # Specify legend font:
    __legendLabelStyle = {'color': '#000', 'size': '7pt', 'bold': True, 'italic': False}
    # Use HTML signature to set title, spacing and font for all charts:
    __titleHTML = "<span style='color: #969696; font-size: 7pt; font-weight: bold; padding-top: 300px'>{PlotName}</span>"
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, *args, **kwargs):
        """
        * Overloaded Constructor. Instantiate new Forward Rate Plot using passed parameters.
        Inputs:
        * configRows: Dictionary mapping curves to their configurations ({CurveName -> CurveConfig}) for all curves that will be used to generate this plot (one plot can have many curves). 
        * plotTitle: Title to use for plot.
        * inputPath: Path object denoting Merlin Curve folder that is subscribed to observer listed in FileContainer object.
        * outputPath: Path object denoting PNG output location that is subscribed to observer listed in FolderContainer object.
        * TMinusOne: T-1 date used to add additional comparison curve to graph.
        * ValueDate: T date used to add initial curve to graph.
        Optional Inputs:
        * TPath: Will overwrite the Merlin Curve input path for T plotted curves.
        * TMinusOnePath: Will overwrite the Merlin Curve input path for T-1 plotted curves.
        """
        args = (args[0] if isinstance(args[0], list) else args)
        if len(args) < 6:
            raise ValueError('ForwardRatePlot construction error: missing some positional arguments.')
        self.CurveConfigs = args[0]
        self.MerlinCurvesPath = args[1]
        self.IntendedOutputPath = args[2]
        self.PlotTitle = args[3]
        self.ValueDate = args[4]
        self.TMinusOne = args[5]
        self.RunTime = self.CurveConfigs[list(self.CurveConfigs.keys())[0]].RunTime
        # Overwrite the T and T-1 Merlin curve paths if passed:
        self.__TPath = kwargs.get('TPath', '')
        self.__TMinusOnePath = kwargs.get('TMinusOnePath', '')

        # Main window for this plot:
        self.__MainWindow = ''
        # Store list of curves that could not be found in production:
        self.__MissingCurves = []
        # Variable indicates whether plot was successfully completed:
        self.FinalOutputPath = ''
    
    ##########################################################
    ## Public Methods:
    ##########################################################
    def GenerateImage(self):
        """
        * Pull in rates data for each loaded curve, plot all into single plot and output to
        location determined by plotting configuration file or command line.
        """
        # Exit if no curve configurations were loaded at construction:
        if self.CurveConfigs is None or len(self.CurveConfigs.keys()) == 0:
            raise NonFatals.NoPlotsLoaded(callingFunc = 'ForwardRatePlot::GenerateImage()', plotTitle = self.PlotTitle)

        ############################
        # Initialize the Plot:
        ############################
        plotOutputLoc = self.IntendedOutputPath
        self.__CreateWindow()
        mainPlot = self.__MainWindow.plotItem
        # Add the legend:
        mainPlot.addLegend()
        # Randomly select color scheme to use for plotting:
        lineColors = ForwardRatePlot.__plotColors[randint(0, len(ForwardRatePlot.__plotColors) - 1)]
        currColor = 0
        # Track all potential curves that can inhabit this graph:
        allCurves = []

        ############################
        # Pull in all discount factors from Merlin generated text file, calculate forward rates and input into plot:
        ############################
        for curve in self.CurveConfigs.keys():
            currCount = 0
            isTMinusOne = self.CurveConfigs[curve].PlotT1
            currDate = self.ValueDate
            curveTitle = curve
            while currCount < 2:
                # Use override paths for Merlin input curves if specified on command line, else use configured path:
                if currCount == 0 and self.__TPath:
                    currPath = self.__TPath
                elif currCount == 1 and self.__TMinusOnePath:
                    currPath = self.__TMinusOnePath
                else:
                    # Use discount factor files specified in configuration file by default:
                    currPath = self.MerlinCurvesPath
                # Get the path to the Merlin curve file: 
                currPath = FileType.ConvertSignature(path = currPath, ValueDate = currDate, CurveName = curve)
                if curveTitle not in allCurves:
                    allCurves.append(curveTitle)
                # Ensure that curve exists at file path:
                if not FileType.CheckPath(currPath):
                    # Append the unique missing curve to the list:
                    if curveTitle not in self.__MissingCurves:
                        self.__MissingCurves.append(curveTitle)
                else:
                    ##############
                    # Pull in discount factors and calculate forward rates: 
                    ##############
                    discountFactors = list(csv.reader(open(currPath, 'r'), delimiter='\t'))
                    # Calculate all forward rates:
                    fwdRates = self.__CalculateForwardRates(discountFactors, curve)
                    ##############
                    # Perform plotting:
                    ##############
                    currCount += 1
                    # Use a dashed line for graph if curve is T-1:
                    currPen = pyqtgraph.mkPen(color = lineColors[currColor], style = (QtCore.Qt.DashLine if currCount == 2 else QtCore.Qt.SolidLine))
                    # Create the plot using the forward rate dates as x series, daily forward rates as y series:
                    mainPlot.plot(fwdRates.keys(), fwdRates.values(), pen=currPen, name=curveTitle)
                # Repeat process if plot needs T-1, using 'T-1' prepended to curve title and T-1 date to pull discount factors:
                if isTMinusOne:
                    curveTitle = 'T-1 ' + curve
                    currDate = self.TMinusOne
                    isTMinusOne = False
                else:
                    # Proceed to next curve if no T-1 curve remains to be plotted:
                    currColor += 1
                    break

        # Prevent graph output if no curves were plotted:
        if len(self.__MissingCurves) == len(allCurves):
            raise NonFatals.FailedToGeneratePNGS(callingFunc = 'ForwardRatePlot::GenerateImage()', plotTitle = self.PlotTitle, specific = 'No curves plotted.')

        ############################
        # Format the plot axes:
        ############################
        # Set font for each axis:
        for axis in ('left','bottom','top','right'):
            mainPlot.getAxis(axis).tickFont = ForwardRatePlot.__axisFont
        for axis in ('left', 'bottom'):
            mainPlot.getAxis(axis).setGrid(255)
        mainPlot.getAxis('bottom').setWidth(4)

        # Format the legend:
        for item in mainPlot.legend.items:
            for single_item in item:
                if isinstance(single_item, pg.graphicsItems.LabelItem.LabelItem):
                    single_item.setText(single_item.text, **ForwardRatePlot.__legendLabelStyle)

        ############################
        # Output the plot to a PNG image:
        ############################
        # Create enclosing folder for plot if does not exist:
        self.CreateFolderIfDoesNotExist(self.ExtractFolderName(plotOutputLoc))

        try:
            exporter = FixedImageExporter.FixedImageExporter(mainPlot)
            exporter.export(plotOutputLoc)
        except Exception as err:
            raise NonFatals.FailedToGeneratePNGS(callingFunc = 'ForwardRatePlot::GenerateImage()', plotTitle = self.PlotTitle, specific = err.message)
        
        # If succeeded, set the object's final output location:
        self.FinalOutputPath = plotOutputLoc
    
        # Raise non-fatal exception if some merlin curves were missing from production locations:
        if len(self.__MissingCurves) > 0:
            raise NonFatals.MerlinCurvesMissing(callingFunc = 'ForwardRatePlot::GenerateImage()', targetList = self.__MissingCurves)

    def __CreateWindow(self):
        """
        * Instantiate the main plot.
        """
        self.__MainWindow = pg.PlotWidget(axisItems={ 'bottom': TimeAxis(orientation='bottom'), 'left' : PercentAxis(orientation='left')})
        # Set title using this plots title: 
        self.__MainWindow.plotItem.setTitle(title = self.PlotTitle, color = '030302', size = '15pt')
        # Position the title to be lower than default value:
        self.__MainWindow.plotItem.titleLabel.item.setPos(250, 10)

    def __SetTitleWithHTML(self, htmlString, titleLabel):
        """
        * Use HTML string to create the plot title.
        """
        self.__MainWindow.plotItem.titleLabel.setMaximumHeight(30)
        self.__MainWindow.plotItem.layout.setRowFixedHeight(0, 30)
        self.__MainWindow.plotItem.titleLabel.setVisible(True)
        self.__MainWindow.plotItem.titleLabel.text = titleLabel
        self.__MainWindow.plotItem.titleLabel.item.setHtml(FileType.ConvertSignature(htmlString, PlotName = self.PlotTitle))
        self.__MainWindow.plotItem.titleLabel.updateMin()
        self.__MainWindow.plotItem.titleLabel.resizeEvent(None)
        self.__MainWindow.plotItem.titleLabel.updateGeometry()

    def __CalculateForwardRates(self, discountFactors, curveName):
        """
        * Calculate forward rates used in plotting.
        Inputs:
        * discountFactors: List containing all raw discount factors from generated Merlin file.
        * curveName: Name of curve associated with discount factors.
        Outputs:
        * fwdRates: OrderedDict containing all calculated forward rates.
        Note: If curve is a BRL currency curve then will use a different forward rate calculation method.
        """
        
        isBRL = (curveName.find('BRL') > -1)
        dayCount = (252 if isBRL else 360)
        fwdRateConv = self.__CurveConfigs[curveName].FwdRateConv
        fwdRateCalcDenom = fwdRateConv / dayCount
        rowNum = 0
        fwdRate = 0
        fwdRates = OrderedDict()
        endIndex = len(discountFactors) - int(fwdRateConv)
        hasZeroFwdRate = False
    
        #####################
        # Calculate all forward rates using discount factors:
        #####################
        while rowNum < endIndex:
            # Calculate BRL curves using different method due to weekend issue:
            if isBRL:
                fwdRate = pow(((float(discountFactors[rowNum][1])) / float(discountFactors[rowNum + int(fwdRateConv)][1])), dayCount) - 1 
            else:
                fwdRate = (float(discountFactors[rowNum][1]) / float(discountFactors[rowNum + int(fwdRateConv)][1]) - 1) / fwdRateCalcDenom

            if fwdRate == 0:
                hasZeroFwdRate = True

            fwdRates[int(discountFactors[rowNum][0])] = fwdRate
            rowNum += 1

        #####################
        # Handle the BRL zero forward rates issue if BRL discount factors were passed:
        #####################
        if isBRL and hasZeroFwdRate:
            startDateSerial = fwdRates.keys()[0]
            # Use first non-zero lagged value:
            for currDateSerial in fwdRates.keys():
                if fwdRates[currDateSerial] == 0:
                    if currDateSerial != startDateSerial:
                        # Use lagged non-zero forward rate:
                        fwdRates[currDateSerial] = fwdRates[currDateSerial - 1]
                    else:
                        # Remove first element if has a 0 forward rate and increment the start date:
                        del fwdRates[currDateSerial]
                        startDateSerial += 1

        return fwdRates

    def __DictToCSV(self, dict, curveName):
        """
        * Output dictionary (presumably containing forward rates) to CSV file.
        """
        filePath = 'K:/Operations/Oberon/Ben R Temp/Merlin Plotting Tool Update/UAT/FwdRates_{CurveName}.txt'
        try:
            with open(FileType.HandleDuplicates(FileType.ConvertSignature(filePath, ForOutput = True, CurveName = curveName)),'w') as outputFile:
                for key in dict.keys():
                    outputFile.write(str(key) + '\t' + str(dict[key]) + '\n')
        except Exception as err:
            print err.message

    ##########################################################
    ## Properties/Setters:
    ##########################################################
    @property
    def CurveConfigs(self):
        """
        * Return the curve configurations container.
        Output:
        * CurveConfigs: Dictionary object that maps { CurveName -> CurveConfigRow }.
        """
        return self.__CurveConfigs
    @property
    def FinalOutputPath(self):
        """
        * Return the output path if successfully generated the image.
        Output:
        * FinalOutputPath: string corresponding to successful output path.
        """
        return self.__FinalOutputPath
    @property
    def IntendedOutputPath(self):
        """
        * Return the output path for the generated image.
        Output:
        * IntendedOutputPath: string that has been converted using this object's state.
        """
        # Return key subscriber attribute if storing an observer object:
        temp = (self.__OutputPath.value if hasattr(self.__OutputPath, 'value') else self.__OutputPath)
        # Incorporate this object's state into the signature, and handle presence of duplicates:
        temp = FileType.ConvertSignature(temp, ValueDate = self.ValueDate, RunTime = self.RunTime, PlotName = self.PlotTitle)
        temp = FileType.HandleDuplicates(temp)

        return temp
    @property
    def MerlinCurvesPath(self):
        """
        * Return the input path for Merlin curves 
        Output:
        * MerlinCurvesPath: signature string that expects to be converted 
        using ValueDate/TMinusOne, Curve Name and other attributes
        """
        # Return key subscriber attribute if storing an observer object:
        return (self.__MerlinCurvesPathSignature.value if hasattr(self.__MerlinCurvesPathSignature, 'value') else self.__MerlinCurvesPathSignature)
    @property
    def PlotTitle(self):
        """
        * Return title of the plot.
        Output:
        * PlotTitle: string containing plot title.
        """
        return self.__PlotTitle
    @property
    def RunTime(self):
        """
        * Return indicator for batch time for all merlin curves on this graph.
        Output:
        * RunTime: string.
        """
        return self.__RunTime
    @property
    def TMinusOne(self):
        """
        * Return the T-1 date.
        Output:
        * TMinusOne: date object for T-1 date.
        """
        return self.__TMinusOne
    @property
    def ValueDate(self):
        """
        * Return the value date.
        Output:
        * ValueDate: date object for Value Date.
        """
        return self.__ValueDate

    @CurveConfigs.setter
    def CurveConfigs(self, value):
        """
        * Set the curve configurations container.
        Input:
        * value: Dictionary object mapping { Curve Name -> Curve Configuration }.
        Must contain at least one key that is a CurveConfigRow.
        """
        try:
            if isinstance(value, dict) and isinstance(value[value.keys()[0]], PlotConfig.CurveConfig):
                self.__CurveConfigs = value
            else:
                self.__CurveConfigs = None
        except Exception as err:
            self.__CurveConfigs = None
    @FinalOutputPath.setter
    def FinalOutputPath(self, value):
        """
        * Set the output path if successfully generated the image.
        Input:
        * value: string only.
        """
        if isinstance(value, str):
            self.__FinalOutputPath = value
        else:
            raise ValueError('FinalOutputPath must be a string.')
    @IntendedOutputPath.setter
    def IntendedOutputPath(self, value):
        """
        * Set the output path for the generated image.
        Input:
        * value: string filepath that has been converted using this object's attributes.
        """
        # Path subscriber objects have "value" as the main attribute:
        if isinstance(value, str) or hasattr(value, 'value'):
            self.__OutputPath = value
        else:
            raise ValueError('IntendedOutputPath must be string or Path subscriber object.')
    @MerlinCurvesPath.setter
    def MerlinCurvesPath(self, value):
        """
        * Set the input path for Merlin curves 
        Input:
        * value: signature string or Path subscriber object that expects to be converted 
        using ValueDate/TMinusOne, Curve Name and other attributes.
        """
        if isinstance(value, str) or hasattr(value, 'value'):
            self.__MerlinCurvesPathSignature = value    
        else:
            raise ValueError('MerlinCurvesPath must be string or Path subscriber object.')
    @PlotTitle.setter
    def PlotTitle(self, value):
        """
        * Set this plot's title.
        Input:
        * value: string corresponding to plot title. 
        """
        if isinstance(value, str):
            self.__PlotTitle = value
        else:
            raise ValueError('PlotTitle must be a string.')
    @RunTime.setter
    def RunTime(self, value):
        """
        * Set the batch time for all Merlin curves placed on the graph.
        Input:
        * value: string that is one of {AM, PM, CAPULA}.
        """
        if isinstance(value, str) and value in ['AM', 'PM', 'CAPULA']:
            self.__RunTime = value
        else:
            raise ValueError('RunTime must be a string and one of {AM, PM, CAPULA}.')
    @TMinusOne.setter
    def TMinusOne(self, value):
        """
        * Set the T-1 date (date object).
        Input:
        * value: date/datetime object or convertible string that must be before the Value Date.
        """
        if isinstance(value, datetime.date) and value < self.ValueDate:
            self.__TMinusOne = value
        elif isinstance(value, datetime.datetime) and value.date() < self.ValueDate:
            self.__TMinusOne = value.date()
        elif isinstance(value, str) and util.StringIsDate(value):
            self.__TMinusOne = datetime.datetime.strptime(value, '%m/%d/%Y').date()
        else:
            raise ValueError('TMinusOne must be a date/datetime/(convertible) string object that is before ValueDate.')
    @ValueDate.setter
    def ValueDate(self, value):
        """
        * Set the value date (date object).
        Input:
        * value: date/datetime object or convertible string.
        """
        if isinstance(value, datetime.date):
            self.__ValueDate = value
        elif isinstance(value, datetime.datetime):
            self.__ValueDate = value.date()
        elif isinstance(value, str) and util.StringIsDate(value):
            self.__ValueDate = datetime.datetime.strptime(value, '%m/%d/%Y').date()
        else:
            raise ValueError('ValueDate must be a date/datetime/(convertible) string object that is before ValueDate.')
    