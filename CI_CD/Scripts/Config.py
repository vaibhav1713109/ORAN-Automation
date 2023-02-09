###############################################################################
##@ FILE NAME:      Configuration File
##@ TEST SCOPE:     M PLANE O-RAN CONFORMANCE \n
##@ Version:        V_1.0.0
##@ Support:        @Ramiyer, @VaibhavDhiman, @PriyaSharma
###############################################################################

###############################################################################
## Package Imports 
###############################################################################

import os, sys
from configparser import ConfigParser

directory_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(directory_path)
sys.path.append(directory_path)
image_path = os.path.dirname(directory_path)

from require.Write_Data import *

########################################################################
## For reading data from .ini file
########################################################################
configur = ConfigParser()
configur.read('{}/Scripts/inputs.ini'.format(directory_path))

def take_input():
    data = {
    'sw_path' : '{0}/LPRU_images/{1}'.format(image_path,sys.argv[1]),
    }
    WriteData(data, '{}/Scripts/inputs.ini'.format(directory_path))
    try:
        os.mkdir('{}/LOGS/{}'.format(directory_path,configur.get('INFO','ru_name_rev')))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    take_input()
    pass




