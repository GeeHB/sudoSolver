# coding=UTF-8
#
#   File     :   keyboard.py
#
#   Author      :   JHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#
#   Version     :   1.2.4
#
#   Date        :   2021-07-21
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