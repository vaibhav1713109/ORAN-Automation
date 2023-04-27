"""
calnexRest.py, version 2.0

This file provides a Python interface to Paragon-Neo and Attero.

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
import requests, hashlib

_LAST_ERR = ""
_INSTRUMENT = ""
_AUTH_TOKEN  = ""
_CAT_TIMEOUT = 60


def _check_for_error(label):
    global _LAST_ERR

    if len(_LAST_ERR) > 0:
        raise Exception("%s : %s" % (label, _LAST_ERR))


def _args_to_json(arg):
    """
    Convert from list to JSON and inject authentication token
    """
    global _AUTH_TOKEN
    
    i = iter(arg)
    dictionary = dict(zip(i, i))
    dictionary["AuthToken"] = _AUTH_TOKEN
    return json.dumps(dictionary)


def calnexInit(ip_addr, **kwargs):
    """
    Initialises the connection to the instrument
    Arguments:
        ip_addr - the IP address of the isntrument
    """
    global _INSTRUMENT
    global _LAST_ERR
    global _AUTH_TOKEN

    _LAST_ERR = ""
    if ip_addr == "":
        _LAST_ERR = "Must specify an IP Address for the instrument"
    else:
        ip_address = ip_addr
        _INSTRUMENT = "http://" + ip_address + "/api/"
        try:
            model = calnexGetVal("instrument/information", "HwType")
            sn = calnexGetVal("instrument/information", "SerialNumber")
            features = calnexGetVal("instrument/options/features", "Features")

            # Authentication
            password = kwargs.get('password', None)
            if ("Authentication" in features):
                if(password==None):
                    _lastErr = "Instrument authentication is enabled, but no password has been supplied"
                else:
                    if (len(password)!=32):
                        password = hashlib.md5(password.encode('utf-8')).hexdigest()
                    _AUTH_TOKEN = calnexGet("authentication/login", "Password", password)["AuthToken"]
            else:
                if(password!=None):
                    print("WARNING: Authentication option not fitted, supplied password not required!")
        except requests.exceptions.RequestException as exc:
            model = "Unknown"
            sn = "Unknown"
            _LAST_ERR = str(exc)
        print("%s %s" % (model, sn))

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
    global _AUTH_TOKEN
    global _LAST_ERR

    _LAST_ERR = ""
    if _INSTRUMENT == "":
        _LAST_ERR = "IP address not configured - call calnexInit before any other calls"
    else:
        try:
            requests.delete(
                "{0}{1}".format(_INSTRUMENT, url),
                data=json.dumps({'AuthToken': _AUTH_TOKEN}),
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
    global _AUTH_TOKEN

    remote_file = os.path.join(src_folder, filename)
    url = \
        "cat/filecommander/download/" + folder_type + \
        "?AsAttachment=true&FileId=" + remote_file
    local_file = os.path.join(dest_folder, filename)
    local_fid = open(local_file, "wb")

    try:
        response = requests.get("{0}{1}".format(_INSTRUMENT, url), data=json.dumps({'AuthToken': _AUTH_TOKEN}))
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

    from datetime import datetime

    def is_link_up(port):
        """ Is the link up on the specified port """
        eth_link = "UNDEFINED"
        link_state = "UNDEFINED"

        leds = calnexGet("results/statusleds")
        if port == 0:
            eth_link = 'ethLink_0'
        else:
            eth_link = 'ethLink_1'

        for led in leds:
            # print (led)
            if led['Name'] == eth_link:
                link_state = led['State']
        if link_state == 'Link':
            return True
        else:
            return False

    def is_good_pkts(port):
        """ Are packets being received on the specified port """
        eth_pkts = "UNDEFINED"
        pkts_state = "UNDEFINED"

        leds = calnexGet("results/statusleds")
        if port == 0:
            eth_pkts = 'ethPkt_0'
        else:
            eth_pkts = 'ethPkt_1'

        for led in leds:
            # print (led)
            if led['Name'] == eth_pkts:
                pkts_state = led['State']
        if pkts_state == 'GoodPackets':
            return True
        else:
            return False

    def is_ref_locked():
        """ Is the frequency reference locked """
        leds = calnexGet("results/statusleds")

        for led in leds:
            # print (led)
            if led['Name'] == 'refInClk':
                state = led['State']
        if state == 'Signal':
            return True
        else:
            return False

    def noise_generation_test(duration_s):
        """ Measure SyncE wander """
        print("--- Noise Generation --------------------------------------------------------")
        # Start SyncE Wander measurement
        calnexSet("app/measurement/synce/wander/Port1/start")

        time.sleep(duration_s)

        # Stop SyncE Wander measurement
        calnexSet("app/measurement/synce/wander/Port1/stop")

        # Enable MTIE and TDEV in the CAT
        # calnexSet("cat/measurement/SyncE/A/MTIE/-/enable", "Value", True)
        # calnexSet("cat/measurement/SyncE/A/TDEV/-/enable", "Value", True)
        calnexSet("cat/measurement/SyncE/A/MTIE/-/isenabled", "Value", True)
        calnexSet("cat/measurement/SyncE/A/TDEV/-/isenabled", "Value", True)

        # Select the G.8262 mask and calculate
        calnexSet("cat/measurement/SyncE/A/MTIE/-/mask",
                  "MaskName", 'G.8262 Wander Generation EEC Op1')
        calnexSet("cat/general/calculate/start")
        calnexIsCatDone()

        # Get the pass/fail result from the CAT
        pf_mtie = calnexGetVal("cat/measurement/SyncE/A/MTIE/-", 'MaskState')
        pf_tdev = calnexGetVal("cat/measurement/SyncE/A/TDEV/-", 'MaskState')

        print("MTIE mask: {}   TDEV mask: {}". format(pf_mtie, pf_tdev))

    # The instrument IP address
    IP_ADDR = "100g-vm8"

    # The interface to test
    INTERFACE = "qsfp28"

    # Connect to the instrument
    calnexInit(IP_ADDR)
    # Print the instrument model
    MODEL = calnexGetVal("/instrument/information", "HwType")
    print(MODEL)

    # Select PTP and leave some time for the preset change
    calnexSet("instrument/preset", "Name", 'SyncE Wander')
    time.sleep(5)
    # Configure the reference - external 10MHz on BNC
    calnexSet("physical/references/in/clock/bnc/select")
    calnexSet("physical/references/in/clock/bnc", "Signal", '10M')
    # Configure the ethernet ports
    calnexSet("physical/port/ethernet/Port1/" + INTERFACE + "/select")

    # Check that the reference is locked
    ref_lock = is_ref_locked()
    if not ref_lock:
        print("Reference is not locked. Aborting...")
        exit(1)
    else:
        print("Reference is locked")

    # Check that the links are up and that we are seeing packets
    port1_link = is_link_up(1)
    port2_link = is_link_up(2)
    if not port1_link or not port2_link:
        print("Links are not up. Aborting...")
        exit(1)
    else:
        print("Links are up")

    port1_pkts = is_good_pkts(1)
    port2_pkts = is_good_pkts(2)
    if not port1_pkts or not port2_pkts:
        print("No packets being received. Aborting...")
        exit(1)
    else:
        print("Packets are being received")

    noise_generation_test(30)       # Should run for ~3000s

    # Generate the report and save it into the same folder as the script
    dt = datetime.today()
    dt_str = dt.strftime("%Y-%m-%dT%H-%M-%S")
    fname = "NoiseGen_" + dt_str + ".pdf"
    calnexCatGenerateReport(fname)
