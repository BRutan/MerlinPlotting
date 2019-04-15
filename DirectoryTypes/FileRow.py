##############################################################################
## FileRow.py
##############################################################################
## Description:
## * Abstract base class used to handle all file content functionality.

from abc import ABCMeta, abstractmethod
import re

__all__ = ['FileRow']

class FileRow(object):
    " Abstract base class for rows in file objects. "
    __metaclass__ = ABCMeta
    
    @classmethod
    def StrToBool(self, entry):
        """ Convert string to boolean value. """
        
        if re.match('^[Tt][Rr][Uu][Ee]$|^[Tt]$', entry):
            return True
        elif re.match('^[Ff][Aa][Ll][Ss][Ee]$|^[Ff]$', entry):
            return False
        else:
            raise ValueError('Could not convert ' + entry + ' to boolean.')

