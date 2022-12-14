#!/bin/python3

import math
import os
import random
import re
import sys

#
# Complete the 'timeConversion' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING s as parameter.
#

def timeConversion(s):
    new_s = ''
    if s[-2:] == 'PM':
        t = int(s[:2])+12
        print(t)
        if t == 24:
            new_s = new_s+'12'+s[2:-2]   
        else: 
            new_s = new_s+str(int(s[:2])+12)+s[2:-2]
    elif s[-2:] == 'AM':
        if s[:2] == '12':
            new_s = new_s+'00'+s[2:-2]
        else:
            new_s = new_s+s[:-2]
    return new_s
    # Write your code here

if __name__ == '__main__':
    # fptr = open(os.environ['OUTPUT_PATH'], 'w')

    s = input()

    result = timeConversion(s)
    print(result)
    # fptr.write(result + '\n')

    # fptr.close()
