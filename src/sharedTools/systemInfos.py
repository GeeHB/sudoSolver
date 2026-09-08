# coding=UTF-8
#
#   File        :   systemInfos.py
#
#   Author      :   GeeHB
#
#   Dependencies :  pygame, pyautogui
#
#   Description :   Informations about the current OS
#
import platform
import subprocess

import pygame
from pygame._sdl2.video import Window

#------------------------------------------------------------------------
#
# Constants
#
#------------------------------------------------------------------------

# Keys
KEY_OS = "Platform"
#KEY_DISTROS = "Distribution"
KEY_WM = "WindowManager"

# Values
VAL_UNKOWN = "Unknown"
VAL_WINDOWS = "Windows"

OS_UNKNOWN = VAL_UNKOWN
OS_WINDOWS = VAL_WINDOWS
OS_LINUX = "Linux"
OS_MACOS = "Darwin"

WM_UNKNOWN = VAL_UNKOWN
WM_WINDOWS = VAL_WINDOWS
WM_CHROMEOS = "Sommelier"
WM_MACOS = "Cocoa"

#------------------------------------------------------------------------
#
# Global variables
#
#------------------------------------------------------------------------

#------------------------------------------------------------------------
#
# Functions
#
#------------------------------------------------------------------------

# System Informations
#
#   Get informations about the OS
#
#   return a dict
#
def getSystemInformations() -> dict[str,str] | None:
    # Default values ...
    current = platform.system()
    myDict = {KEY_OS : current, KEY_WM : WM_UNKNOWN}

    # Try to get the Windows Manager name
    if current == OS_WINDOWS:
        # On windows, all is "Windows"
        myDict[KEY_WM] = WM_WINDOWS
    else:
        if current == OS_MACOS:
            myDict[KEY_WM] = WM_MACOS
        else:
            try:
                output = subprocess.run(['wmctrl', '-m'], text=True,
                                    capture_output=True, check = False)
                if output.stderr:
                    print("Unable to retreive window manager name")
                    return

                # Found it !!
                lines = output.stdout.split("\n")
                if len(lines) > 1:
                    line = lines[0]
                    myDict[KEY_WM] = line[line.rfind(" ")+1:]
            except FileNotFoundError:
                # Unable to load the module
                pass

    # Finished
    return myDict

# Get the position of current Window
#
# returns (x,y) in screen coordinates
#
def getMainWindowPosition()->tuple[int,int] | None:
    myDict = getSystemInformations()

    # On linux ?
    if myDict[KEY_OS] == OS_LINUX:  # pyright: ignore[reportOptionalSubscript]
        #return Window.from_display_module().position
        return None
    else:
        # Windows ?
        if myDict[KEY_OS] == OS_WINDOWS:  # pyright: ignore[reportOptionalSubscript]
            try:
                from ctypes import POINTER, WINFUNCTYPE, windll
                from ctypes.wintypes import BOOL, HWND, RECT
            except ModuleNotFoundError:
                return None

            # Get the Window Handle
            hwnd = pygame.display.get_wm_info()["window"]

            # Specify Win32 API
            prototype = WINFUNCTYPE(BOOL, HWND, POINTER(RECT))
            paramflags = (1, "hwnd"), (2, "lprect")
            GetWindowRect = prototype(("GetWindowRect", windll.user32), paramflags)

            # Call the function
            rect = GetWindowRect(hwnd)
            return (rect.left, rect.top)

    return (0,0)    # !!!

# Set the position of current Window
#
#   @position is a (x,y) tuple
#
def setMainWindowPosition(position : tuple[int, int] | None):
    if position is not None :
        myDict = getSystemInformations()

        # On linux ?
        if myDict[KEY_OS] == OS_LINUX:  # pyright: ignore[reportOptionalSubscript]
            Window.from_display_module().position = position
        else:
            # Windows ?
            if myDict[KEY_OS] == OS_WINDOWS:  # pyright: ignore[reportOptionalSubscript]
                try:
                    from ctypes import POINTER, WINFUNCTYPE, windll
                    from ctypes.wintypes import BOOL, HWND, RECT
                except ModuleNotFoundError:
                    return

                # Get the Window Handle
                hwnd = pygame.display.get_wm_info()["window"]

                # Specify Win32 API
                SetWindowPos = windll.user32.SetWindowPos

                # Call the API
                SetWindowPos(hwnd, 0, position[0], position[1], 0, 0, 0x0005) # No topmost, move | nosize

# Get desktop size
#
#   Rem : Return the dimensions en pixels of the main desktop
#
#   return a tuple (width, height) or None if error
#
def getDesktopSize(desktopIndex : int | None = None)->tuple[int,int] | None:
    info = getSystemInformations()

    try:
        if info[KEY_OS] != OS_MACOS:  # pyright: ignore[reportOptionalSubscript]
            import tkinter

            app = tkinter.Tk()
            return (app.winfo_screenwidth(), app.winfo_screenheight())
        else:
            # MacOS - BUG : tkinter mainwindow always visible
            import pyautogui
            a = pyautogui.size()
            return (a.width, a.height)

    except ModuleNotFoundError:
        # no tkinter
        return None

    # ???
    return None

# EOF
