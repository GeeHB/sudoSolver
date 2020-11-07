
# coding=UTF-8
#
#   File     :   keyboard.py
#
#   Author      :   JHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#
#   Version     :   0.1.26-6
#
#   Date        :   2020-09-29
#

import msvcrt
import keyboard

class msKeyboard(keyboard.keyboard):

    # Read the keyboard
    # returns  a  char
    def getChar(self):
         return msvcrt.getch()

#EOF
    