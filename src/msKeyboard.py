# coding=UTF-8
#
#   File        :   keyboard.py
#
#   Author      :   GeeHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#

from ownExceptions import sudokuError

try:
    import msvcrt
except ModuleNotFoundError:
    raise sudokuError("msvcrt module is not installed")

import keyboard


class msKeyboard(keyboard.keyboard):

    # Read the keyboard
    # returns  a  char
    def getChar(self):
         return msvcrt.getch()

#EOF