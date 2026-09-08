# coding=UTF-8
#
#   File        :   pointer.py
#
#   Author      :   GeeHB
#
#   Description :   "pointer" object definition
#

import math

from ownExceptions import reachedEndOfList

# shared consts
#
ROW_COUNT = LINE_COUNT = 9

GRID_SIZE = ROW_COUNT * LINE_COUNT

VALUE_MIN = 1
VALUE_MAX = LINE_COUNT

INDEX_MIN = 0
INDEX_MAX = (GRID_SIZE - 1)

#
# pointer - "ID" of an element in the sudoku's grid
#
#   This object does all the conversion from linear index to matrix coordinates
#
class pointer:
    # Construction
    #
    def __init__(self, index:int | None = None, gameMode:bool = True):
        self.index_:int  = INDEX_MIN if index is None else index
        self.row_:int = 0
        self.line_:int = 0
        self.squareID_:int = 0
        self.gameMode_:bool = gameMode

        self._whereAmI()

    def __repr__(self)->str:
        return f"index : {self.index_}\n\t- pos : ({self.row_} x {self.line_})\n\t-square ID : {self.squareID_}"

    # Absolute position
    #
    def moveTo(self, line:int = 0, row:int = 0, pos:tuple[int,int] | None = None):
        if pos is None:
            # Ensure position is in the grid
            self.row_ = self._setInRange(row)
            self.line_ = self._setInRange(line)
        else:
            # Mouse click outside the grid ?
            if not self._inRange(pos[0]) or not self._inRange(pos[1]):
                # Outside the grid => ignore the click
                return

            self.row_ = pos[0]
            self.line_ = pos[1]

        self.index_ = self.row_ + self.line_ * ROW_COUNT
        self._whereAmI(False)

    # Access
    #
    def index(self)->int:
        return self.index_

    def row(self)->int:
        return self.row_

    def line(self)->int:
        return self.line_

    def squareID(self)->int:
        return self.squareID_

    #
    # Change index
    #

    # +=
    #
    def __iadd__(self, inc:int):
        self.index_ += inc
        # Reach the end of the matrix ?
        if self.index_ > INDEX_MAX:
            if True == self.gameMode_ :
                raise reachedEndOfList
            else:
                if self.index_ > (1+INDEX_MAX):
                    raise IndexError

        self._whereAmI()
        return self

    # -=
    #
    def __isub__(self, dec:int):
        self.index_ -= dec
        if self.index_ < INDEX_MIN:
            raise IndexError

        self._whereAmI()
        return self

    # Change "row"
    #
    def decRow(self, dec:int = 1):
        row = self.row_ - dec
        if row < 0:
            self.index_ = (1 + self.line_ ) * ROW_COUNT + row
        else:
            self.index_ -= dec
        self._whereAmI()

    def incRow(self, inc:int = 1):
        row = self.row_ + inc
        if row >= ROW_COUNT:
            self.index_ = (self.line_ - 1) * ROW_COUNT + row
        else:
            self.index_ += inc
        self._whereAmI()

    # Change "line"
    #
    def decLine(self, dec:int = 1):
        self.index_ -= ROW_COUNT * dec
        if self.index_ < INDEX_MIN:
            self.index_ = self.row_ + (ROW_COUNT - 1) * ROW_COUNT
        self._whereAmI()

    def incLine(self, inc:int = 1):
        self.index_ += ROW_COUNT * inc
        if self.index_ > INDEX_MAX:
            self.index_ = self.row_
        self._whereAmI()

    #
    # Change the value
    #

    def incValue(self, value:int)->int:
        newVal = value + 1
        return (VALUE_MIN - 1) if newVal > VALUE_MAX else newVal

    def decValue(self, value:int)->int:
        newVal = value - 1
        return VALUE_MAX if newVal < (VALUE_MIN - 1) else newVal

    #
    #   internal methods
    #

    # Updating coordinates
    #
    def _whereAmI(self, all:bool = True):
        if True == all:
            # V. math
            self.line_ = math.floor(self.index_ / ROW_COUNT)
            self.row_ = self.index_ - ROW_COUNT * self.line_

        # Small square ID
        self.squareID_ = 3 * math.floor(self.line_ / 3) + math.floor(self.row_ / 3)

    # Check position
    #
    def _inRange(self, value:int, min:int = 0, max:int = ROW_COUNT - 1)->bool:
        return not (value < min or value > max)

    def _setInRange(self, value:int):
        return 0 if value < 0 else (ROW_COUNT - 1) if value >= ROW_COUNT else value

# EOF
