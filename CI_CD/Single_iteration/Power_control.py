import sys
import os

if len(sys.argv) != 2 or sys.argv[1] not in ['ON', 'OFF']:
    print("Usage: python Power_control.py <ON|OFF>")
    sys.exit(1)

if sys.argv[1] == 'ON':
    command = 'curl -u admin:rpsadmin http://172.25.96.188/rps?SetPower=1+1'
else:
    command = 'curl -u admin:rpsadmin http://172.25.96.188/rps?SetPower=1+0'

os.system(command)

