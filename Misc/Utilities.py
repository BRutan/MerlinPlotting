##############################################################################
## Utilities.py
##############################################################################
## Description:
## * Utility functions to assist key plotting and data generation functions.

import datetime 
import re
import os
import sys

__all__ = ['xldate_to_datetime', 'StringIsDate', 'GetTMinusOne', 'FirstMatchIndex', 'StrIsBool', 'PrintPercentageInPlace']

def xldate_to_datetime(xldate):
    """
    * Convert Excel serial date format into datetime object.
    Input:
    * xlDate: Integer in (0, inf) that represents # of days past Jan 1st, 1900.
    Output:
    * temp + delta: Datetime object corresponding to Excel serial date.
    """
    temp = datetime.datetime(1900, 1, 1)
    delta = datetime.timedelta(days=xldate)
    return temp+delta

def StringIsDate(dateString, time = False, raiseOrReturn = False):
    """
    * Return true if passed string is a date.
    Input:
    * dateString: String that could possibly represent a date.
    * time: Pass True if want to include time (MM/DD/YYYY HH:MM:SS) in string.
    * raiseOrReturn: If True then will raise exception if dateString is not convertible to a date, else will 
    return the string itself.
    Output:
    * Return true if passed date can be converted to a datetime object.
    """
    try:
        datetime.datetime.strptime(dateString, ("%m/%d/%Y %H:%M:%S" if time else "%m/%d/%Y")).date()
        return (dateString if raiseOrReturn else True)
    except:
        if raiseOrReturn:
            raise ValueError
        return False

def GetTMinusOne(ValueDate):
    """
    * Return datetime object that represents first non-weekend day before passed date.
    Input:
    * ValueDate: datetime object or valid string that requires first T-1 date.
    Output:
    * TMinusOne: First non-weekend date before ValueDate.
    """
    if isinstance(ValueDate, str) and not StringIsDate(ValueDate):
        raise ValueError("Could not convert %s to datetime." % ValueDate)
    elif isinstance(ValueDate, str):
        # Convert ValueDate into a datetime object:
        ValueDate = datetime.datetime.strptime(ValueDate, '%m/%d/%Y')
    elif not isinstance(ValueDate, datetime.datetime) and not isinstance(ValueDate, datetime.date):
        raise ValueError("Please pass a string, datetime or date object to Utilities::GetTMinusOne().")
    
    TMinusOne = ValueDate - datetime.timedelta(days = 1)
    while TMinusOne.weekday() >= 5:
        TMinusOne -= datetime.timedelta(days = 1)
    return TMinusOne

def FirstMatchIndex(targetList, regex):
    """
    * Return index of first match for passed regex in the targetList.
    Input:
    * targetList: List object containing strings.
    * regex: Regular expression pattern string.
    Output:
    * index: Index for first match in list. If could not find any elements matching 
    regex pattern then return -1.
    """
    for index in range(1, len(targetList)):
        if regex.match(targetList[index]):
            return index
    # Return -1 if not found:
    return -1

def StrToBool(entry):
    """ Convert string to boolean value. """
        
    if re.match('^[Tt][Rr][Uu][Ee]$|^[Tt]$', entry):
        return True
    elif re.match('^[Ff][Aa][Ll][Ss][Ee]$|^[Ff]$', entry):
        return False
    else:
        raise ValueError('Could not convert ' + entry + ' to boolean.')

def PrintPercentageInPlace(percentage, line = '{0:.1f}%%\r', percentRule = 1):
    """ 
    * Print a percentage or another line in place at current position on the command line. 
    Input: 
    * percentage: Expecting a floating point number.
    * line: Expecting string to be used in formatting the line.
    * percentRule: Integer value where if percentage is divisible by it, then will get printed.
    By default all percentages will be printed.
    """
    if not isinstance(line, str):
        line = '{0:.1f}%%\r'

    plusMinus = 2
    if int(percentage * 100) % percentRule == 0 or int((percentage - plusMinus) * 100) % percentRule == 0 or int((percentage + plusMinus) * 100) % percentRule == 0: 
        sys.stdout.write(line.format(percentage * 100))
        sys.stdout.flush()
