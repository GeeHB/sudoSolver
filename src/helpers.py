# coding=UTF-8
#
#   File        :   helpers.py
#
#   Author      :   GeeHB
#
#   Description :   Helps and advices to the player
#

from enum import IntEnum

from sharedTools import statusbits


# Array complexity - ie. count of filled elements
#
class visualHelp(IntEnum):
    NO_HELP = 0
    SHOW_MATRIX = 1
    SHOW_COLS_AND_LINES = 2
    HIGHLIGHT_VALUE = 4

# helpers :  handle all help available to the player
#
class helpers:
    # Construction
    def __init__(self, status:visualHelp = visualHelp.NO_HELP):
        self.status_:statusbits.statusBits = statusbits.statusBits(status)

        self.fontSize_:int = 0
        self.squareWidth_:int = 0
        self.offsets_:tuple[int,int] = (0,0)

    #
    # Properties
    #

    # Help matrix
    @property
    def showMatrix(self)->bool:
        return self.status_.isSet(visualHelp.SHOW_MATRIX)
    @showMatrix.setter
    def showMatrix(self, value:bool):
        self.status_.set(visualHelp.SHOW_MATRIX, value)

    # col. and line
    @property
    def showColAndLine(self)->bool:
        return self.status_.isSet(visualHelp.SHOW_COLS_AND_LINES)
    @showColAndLine.setter
    def showColAndLine(self, value:bool):
        self.status_.set(visualHelp.SHOW_COLS_AND_LINES, value)

    # Highlight the current value in the grid
    @property
    def highLightValue(self)->bool:
        return self.status_.isSet(visualHelp.HIGHLIGHT_VALUE)
    @highLightValue.setter
    def highLightValue(self, value:bool):
        self.status_.set(visualHelp.HIGHLIGHT_VALUE, value)

# EOF
