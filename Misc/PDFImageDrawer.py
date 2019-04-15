##############################################################################
## PDFImageDrawer.py
##############################################################################
## Description:
## * Object wraps reportlab canvas object to draw images to a PDF.

import reportlab.lib.pagesizes as sizes
from reportlab.pdfgen import canvas
from reportlab.platypus import Image, SimpleDocTemplate
import Exceptions.NonFatal as NonFatals
from math import sqrt

__all__ = ['PDFImageDrawer']

class PDFImageDrawer:
    " Object draws images to pdf and ensures that they are evenly spaced. "
    ##########################################################
    ## Constructors:
    ##########################################################
    def __init__(self, **kwargs):
        """
        * Overloaded Constructor. Instantiate new Forward Rate Plot using passed parameters.
        Optional Inputs:
        * imagesPerSheet: Specify # of images that appear on each sheet.
        * pageSize: sizes object to specify the pdf page size.
        """
        # Set plot height and width within PDF:
        self.pageSize = kwargs.get("pageSize", sizes.A4)
        self.landScape = kwargs.get("Landscape", False)
        # Ensure that types were correct, if not then use default values:
        if not isinstance(self.pageSize, tuple):
            self.pageSize = sizes.A4
        if not isinstance(self.landScape, bool):
            self.landScape = False
        # Instantiate the target PDF:
        self.__targetPDF = None
        self.__path = ''

    ##########################################################
    ## Class Methods:
    ##########################################################
    def InitiatePDF(self, path):
        """
        Instantiate the pdf canvas object, which will be saved to provided path.
        Inputs:
        * path: String path where PDF will be saved.
        """
        self.__path = path
        self.__targetPDF = canvas.Canvas(self.__path, self.pageSize)

    def Draw(self, images, **kwargs):
        """
        Output all images to sheet  
        Inputs:
        * images: List of string paths to PNGs that will be written into the PDF.
        """
        if not isinstance(images, list):
            raise ValueError(message = "'images' must be a list.")
        # Get optional arguments and set to defaults if necessary:
        imagesPerSheet = kwargs.get("MaxImagesPerSheet", 4)
        imagesPerRow = kwargs.get("MaxImagesPerRow", 2)
        if not isinstance(imagesPerSheet, int):
            imagesPerSheet = 4
        if not isinstance(imagesPerRow, int):
            imagesPerRow = 2
        # Get maximum dimensions of sheet:
        xMax, yMax = self.pageSize
        # Calculate border padding from page margins using fixed 2.5%:
        xBorderPadding, yBorderPadding = (xMax * .025, yMax * .025)
        xStart, yStart = (xBorderPadding, yMax - yBorderPadding)
        rowsPerSheet = imagesPerSheet / int(imagesPerRow)
        # Store (xStep, yStep):
        gridSize = (float(xMax) / float((len(images) if len(images) < imagesPerRow else imagesPerRow)), float(yMax) / float(rowsPerSheet))
        center = (gridSize[0] / 2, gridSize[1] / 2)
        # Calculate width and height of image within each cell:
        plotWidth = (center[0] - 2 * xBorderPadding) * 1.1
        plotHeight = center[1] - 2 * yBorderPadding
        ########################
        # Determine preferential spacing based upon # of images per sheet:
        ########################
        # Create mapping object to map { Image # -> (Row #, x) }:
        x, y = (xStart, yStart)
        for imagePath in images:
            self.__targetPDF.drawImage(imagePath, x, y, plotWidth, plotHeight)
            return
        
        plotCount = 0
        rowCount += 1
        imageToPosMap = {}
        while plotCount < self.imagesPerSheet:
            # Increment the row # where image will appear if max # of images
            if plotCount % maxRowImageCount == 0:
                rowCount += 1
            imageToPosMap[plotCount] = (0, 0)
            plotCount += 1
        x, y = (xStart, yStart)
        plotCount = 0
        ########################
        # Add all images at predetermined locations:
        ########################
        for imagePath in images:
            # Set image position:
            if plotCount != newRowCount:
                # Increment the x position:
                x += xStep
            elif plotCount == newRowCount:
                # Increment the y position and reset the x position to start new row:
                x = xStart
                y += yStep
            # Draw image at (x, y) coordinate: 
            self.__targetPDF.drawImage(imagePAth, x, y, plotWidth, plotHeight)
            plotCount += 1
            plotCount %= imagesPerSheet
            # Add new page if added 4 plots:
            if plotCount == 0:
                self.__targetPDF.showPage()


    def SavePDF(self):
        """
        Save the PDF at instantiated location.
        """
        if not isinstance(self.__targetPDF, canvas.Canvas):
            raise NonFatals.FailedToGeneratePDF(self.__path, "PDFImageDrawer::SavePDF()")
        # Attempt to save the PDF:
        try:
            self.__targetPDF.save()
        except Exception as err:
            raise NonFatals.FailedToGeneratePDF(self.__path, "PDFImageDrawer::SavePDF()")
        finally:
            # Reset the object state:
            self.__targetPDF = None
            self.__path = ''
            
    ##########################################################
    ## Class Properties:
    ##########################################################