
# coding=UTF-8
#
#   File     :   keyboard.py
#
#   Author      :   JHB
#
#   Description :   msKeyoard : handle keyboard (ms way)
#
#   Version     :   0.1.26-7
#
#   Date        :   2020-11-14
#

import msvcrt
import keyboard

class msKeyboard(keyboard.keyboard):

    # Read the keyboard
    # returns  a  char
    def getChar(self):
         return msvcrt.getch()

#EOF
    