"""
calnexRest.py, version 2.0

This file provides a Python interface to Paragon-neo.

Changes -----------------------------------------------------------------------
Version 2.0, 19 Feb 2020:
    Added a number of help functions for downloading reports
"""

###############################################################################
#   Copyright (c) Calnex Solutions Ltd 2008 - 2020                            #
#                                                                             #
#   The contents of this file should not be copied or distributed             #
#   without permission being granted by Calnex Solutions Ltd.                 #
#                                                                             #
#   All rights reserved.                                                      #
#                                                                             #
###############################################################################

import os
import time
import json
import requests

_LAST_ERR = ""
_INSTRUMENT = ""
_CAT_TIMEOUT = 60


def _check_for_error(label):
    global _LAST_ERR

    if len(_LAST_ERR) > 0:
        raise Exception("%s : %s" % (label, _LAST_ERR))


def _args_to_json(arg):
    """
    Convert from list to JSON
    """
    i = iter(arg)
    dictionary = dict(zip(i, i))
    return json.dumps(dictionary)


def calnexInit(ip_addr):
    """
    Initialises the connection to the instrument
    Arguments:
        ip_addr - the IP address of the isntrument
    """
    global _INSTRUMENT
    global _LAST_ERR

    _LAST_ERR = ""
    if ip_addr == "":
        _LAST_ERR = "Must specify an IP Address for the instrument"
    else:
        ip_address = ip_addr
        _INSTRUMENT = "http://" + ip_address + "/api/"
        try:
            model = calnexGetVal("instrument/information", "HwType")
            sn = calnexGetVal("instrument/information", "SerialNumber")
        except requests.exceptions.RequestException as exc:
            model = "Unknown"
            sn = "Unknown"
            _LAST_ERR = str(exc)
        print("******Connection Established with %s ****** \nSerial Number: %s" % (model, sn))

    _check_for_error("calnexInit")


def calnexGet(url, *arg):
    """
    Read the specified setting from the connected instrument
    """
    global _INSTRUMENT
    global _LAST_ERR

    _LAST_ERR = ""
    if _INSTRUMENT == "":
        _LAST_ERR = "IP address not configured - call calnexInit before any other calls"
        ret = ""
    else:
        try:
            response = requests.get(
                "{0}{1}?format=json".format(_INSTRUMENT, url),
                data=_args_to_json(arg),
                headers={'Content-Type': 'application/json'})
            response.raise_for_status()
            ret = response.json()
        except requests.exceptions.RequestException as exc:
            _LAST_ERR = str(exc)

    _check_for_error("calnexGet %s" % (url))
    return ret


def calnexGetVal(url, arg):
    """
    Read a setting from the connected instrument and return a specified value
    """
    global _INSTRUMENT
    global _LAST_ERR
    res = calnexGet(url, arg)
    ret = res
    if arg not in res:
        _LAST_ERR = "\"" + arg + "\" does not exist in response: " + str(res)
    else:
        ret = res[arg]

    _check_for_error("calnexGetVal %s %s" % (url, arg))
    return ret


def calnexSet(url, *arg):
    """
    Write to a setting in the connected instrument
    """
    global _INSTRUMENT
    global _LAST_ERR

    _LAST_ERR = ""
    if _INSTRUMENT == "":
        _LAST_ERR = "IP address not configured - call calnexInit before any other calls"
    else:
        try:
            requests.put(
                "{0}{1}?format=json".format(_INSTRUMENT, url),
                _args_to_json(arg),
                headers={'Content-Type': 'application/json'}
                ).raise_for_status()
        except requests.exceptions.RequestException as exc:
            _LAST_ERR = str(exc)
    _check_for_error("calnexSet %s" % (url))


def calnexCreate(url, *arg):
    """ TBD """
    global _INSTRUMENT
    global _LAST_ERR

    _LAST_ERR = ""
    if _INSTRUMENT == "":
        _LAST_ERR = "IP address not configured - call calnexInit before any other calls"
    else:
        try:
            requests.post(
                "{0}{1}".format(_INSTRUMENT, url),
                _args_to_json(arg), headers={'Content-Type': 'application/json'}
                ).raise_for_status()
        except requests.exceptions.RequestException as exc:
            _LAST_ERR = str(exc)
    _check_for_error("calnexCreate %s" % (url))


def calnexDel(url):
    """ TBD """
    global _INSTRUMENT
    global _LAST_ERR

    _LAST_ERR = ""
    if _INSTRUMENT == "":
        _LAST_ERR = "IP address not configured - call calnexInit before any other calls"
    else:
        try:
            requests.delete(
                "{0}{1}".format(_INSTRUMENT, url),
                headers={'Content-Type': 'application/json'}).raise_for_status()
        except requests.exceptions.RequestException as exc:
            _LAST_ERR = str(exc)
    _check_for_error("calnexDel %s" % (url))

#
# Old syntax - kept for backwards compatibility
#


def p100get(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    return calnexGet(url, *arg)


def p100set(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    calnexSet(url, *arg)


def p100create(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    calnexCreate(url, *arg)


def p100del(url):
    """ Compatibility alias for matching calnexXXX """
    calnexDel(url)


def a100get(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    return calnexGet(url, *arg)


def a100set(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    calnexSet(url, *arg)


def a100create(url, *arg):
    """ Compatibility alias for matching calnexXXX """
    calnexCreate(url, *arg)


def a100del(url):
    """ Compatibility alias for matching calnexXXX """
    calnexDel(url)


# Utility functions ####################################

def calnexIsCatDone():
    """ Wait for the CAT to finish opening files and processing data
    Arguments:
        None
    Results:
        Returns True when the CAT no longer indicates that it is
        processing or opening a file.
        The polling period is 1 second with a meximum of 60 re-tries.
        If the re-try count is exceeded, False is returned.
    """
    global _CAT_TIMEOUT

    cat_status = calnexGet("/cat/general/status")
    cat_currently_processing = cat_status["IsApiCurrentlyProcessing"]
    cat_opening = cat_status["IsOpeningInProgress"]
    retry = 0

    while cat_currently_processing or cat_opening:
        time.sleep(1)
        cat_status = calnexGet("/cat/general/status")
        cat_currently_processing = cat_status["IsApiCurrentlyProcessing"]
        cat_opening = cat_status["IsOpeningInProgress"]
        retry = retry + 1
        if retry > _CAT_TIMEOUT:
            return False
    return True


def calnexDownloadFile(folder_type, src_folder, filename, dest_folder):
    """
    Download a file from the instrument
    Arguments:
        folderType	str
            "SessionsFolder" or "ReportFolder"
        srcFolder	str
            The name of the folder on the instrument. For sessions files
            this is the name of the session folder e.g. Session_<date>
        file 		str
            The name of the file - for capture files, this is the name of
            the file in the Session folder
        destFolder	str
            The name of the folder on the local machine where the
            remote file will be saved
    Results:
        Raises an error if the file cannot be found on the instrument
        If the local file or folder can't be accessed then Python will raise a
        file access error
    """
    global _LAST_ERR
    global _INSTRUMENT

    remote_file = os.path.join(src_folder, filename)
    url = \
        "cat/filecommander/download/" + folder_type + \
        "?AsAttachment=true&FileId=" + remote_file
    local_file = os.path.join(dest_folder, filename)
    local_fid = open(local_file, "wb")

    try:
        response = requests.get("{0}{1}".format(_INSTRUMENT, url))
        response.raise_for_status()
        local_fid.write(response.content)
    except requests.exceptions.RequestException as exc:
        _LAST_ERR = str(exc)

    local_fid.close()

    _check_for_error(
        "calnexDownloadFile: Unable to download " + filename
        + " from " + src_folder)

    return


def calnexCatGenerateReport(report_name,
                            dest_folder="./", with_charts=True):
    """
    Generate a report in the CAT and then download it to the local PC
    The measurement must have been stopped before a report can be generated

    Parameters:
        reportName: str
            The name of the report to be generated
        destFolder: str, optional
            The name of the folder on the local PC where the report will
            be saved. The path to the folder will be created if required.
            If destFolder is not specified then the report will be
            saved in the current working directory (i.e. where
            the script is executing)
        withCharts: bool, optional
            If True (the default), then charts will be included in the report.
    Returns:
        None
    Raises:
       Raises a runtime exception if the CAT remains busy
    """
    if calnexIsCatDone():
        calnexGet("/cat/report/data")
        calnexCreate("/cat/report", "RenderCharts", with_charts,
                     "ReportFilename", report_name)

        # Report is now generated. Download it.
        calnexDownloadFile(
            "ReportFolder", "./", report_name, dest_folder)

    else:
        raise RuntimeError(
            "Unable to generate report. CAT is still processing.")


# Simple example and used for testing
if __name__ == "__main__":
    pass
