# coding=UTF-8
#
#   File        :   keyboard.py
#
#   Author      :   GeeHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#
from typing import override

import ownKeyboard
from ownExceptions import sudokuError

try:
    import msvcrt
except ModuleNotFoundError:
    raise sudokuError("msvcrt module is not installed")

class msKeyboard(ownKeyboard.myKeyboard):

    # Read the keyboard
    # returns  a  char
    @override
    def getChar(self) -> str:
         return f"{msvcrt.getch()!r}"

#EOF
