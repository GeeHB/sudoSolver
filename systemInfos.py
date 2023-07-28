# coding=UTF-8
#
#   File        :   systemInfos.py
#
#   Author      :   GeeHB
#
#   Description :   Informations about the current OS
#
import platform, subprocess

# A few constants
#

# Keys
KEY_OS = "Platform"
#KEY_DISTROS = "Distribution"
KEY_WM = "WindowManager"

# Values
VAL_UNKOWN = "Unknown"
VAL_WINDOWS = "Windows"

OS_UNKNOWN = VAL_UNKOWN
OS_WINDOWS = VAL_WINDOWS

WM_UNKNOWN = VAL_UNKOWN
WM_WINDOWS = VAL_WINDOWS
WM_CHROMEOS = "Sommelier"

# System Informations
#
#   return a dict
# 
def getSystemInformations():
    
    # Default values ...
    myDict = {KEY_OS : OS_UNKNOWN, KEY_WM : WM_UNKNOWN}

    current = platform.system()
    if current == "windows":
        # On windows, all is "Windows"
        myDict[KEY_OS] = OS_WINDOWS
        myDict[KEY_WM] = WM_WINDOWS
        return
    
    myDict[KEY_OS] = current

    # Try to get the Windows Manager name
    output = subprocess.run(['wmctrl', '-m'], text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if output.stderr:
        print("Unable to retreive window manager name")
        return
    
    # Found it !!
    lines = output.stdout.split("\n")
    if lines is not None and len(lines) > 1:
        line = lines[0]
        myDict[KEY_WM] = line[line.rfind(" ")+1:]

    return myDict

# EOF