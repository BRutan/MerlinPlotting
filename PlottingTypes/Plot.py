##############################################################################
## Plot.py
##############################################################################
## Description:
## * Abstract base class for plotting objects.

from abc import ABCMeta, abstractmethod
import datetime

__all__ = ['Plot']

class Plot(object):
    " Abstract base class for all plot related objects. "
    __metaclass__ = ABCMeta

    @classmethod
    def ExcelSerialToDatetime(self, xldate):
        """ Convert Excel serial date to a datetime object. """
        temp = datetime.datetime(1900, 1, 1)
        delta = datetime.timedelta(days=int(xldate))
    
        return temp+delta
