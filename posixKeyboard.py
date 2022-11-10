# coding=UTF-8
#
#   File        :   posixKeyboard.py
#
#   Author      :   GeeHB
#
#   Description :   posixKeyoard : handle keyboard
#

import os, sys, termios, fcntl
import keyboard

class posixKeyboard(keyboard.keyboard):
    
    # Read the keyboard
    # returns  a  char
    def getChar(self):

        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:        
            while True:            
                try:
                    c = sys.stdin.read(1)
                    break
                except IOError: 
                    pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        return c
# EOF