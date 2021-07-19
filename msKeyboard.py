
# coding=UTF-8
#
#   File     :   keyboard.py
#
#   Author      :   JHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#
#   Version     :   1.1.2
#
#   Date        :   2021-07-19
#

import msvcrt
import keyboard

class msKeyboard(keyboard.keyboard):

    # Read the keyboard
    # returns  a  char
    def getChar(self):
         return msvcrt.getch()

#EOF