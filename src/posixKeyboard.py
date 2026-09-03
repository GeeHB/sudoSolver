# coding=UTF-8
#
#   File        :   posixKeyboard.py
#
#   Author      :   GeeHB
#
#   Description :   posixKeyoard : handle keyboard
#

import fcntl
import os
import sys
import termios
from typing import override

import ownKeyboard


class posixKeyboard(ownKeyboard.myKeyboard):

    # Read the keyboard
    # returns  a  char
    @override
    def getChar(self) -> str:
        c = ''
        fd = sys.stdin.fileno()
        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        _ = fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

        try:
            while True:
                try:
                    c = sys.stdin.read(1)
                    break
                except OSError:
                    pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            _ = fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
        return c
# EOF
