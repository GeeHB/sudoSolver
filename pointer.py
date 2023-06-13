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

#
# pointer - "ID" of an element in the sudoku's grid
#
#   This object does all the conversion from linear index to matrix coordinates
#
class pointer(object):

    ROW_COUNT = 9
    LINE_COUNT = 9

    VALUE_MIN = 1
    VALUE_MAX = 9

    INDEX_MIN = 0
    INDEX_MAX = (ROW_COUNT * LINE_COUNT - 1)

    # Members
    #
    index_      =   INDEX_MIN       # Current index
    
    row_ = 0                        # Position in the "matrix"
    line_ = 0
    
    squareID_ = 0                   # tiny-square ID

    gameMode_ = False               # In game mode when the end of the matrix is reached, the sudoku is solved !

    # Construction
    #
    def __init__(self, other = None, index = None, gameMode = True):
        # Copy ?
        #
        if not None == other:
            self.set(other)
        else:
            self.index_ = 0 if None == index else index
            self.gameMode_ = gameMode 

            self._whereAmI()

    # Copy constrcutor
    #
    def set(self, other):
        if type(other) is pointer:
            self.index_ = other.index_
            self.row_ = other.row_
            self.line_ = other.line_
            self.squareID_ = other.squareID_
            self.gameMode_ = other.gameMode_

    # Absolute position
    #
    def moveTo(self, line = 0, row = 0, pos = None):
        self.line_ = self._setInRange(line if pos is None else pos[1])
        self.row_ = self._setInRange(row if pos is None else pos[0])
        self.index_ = self.row_ + self.line_ * self.ROW_COUNT

        self._whereAmI(False)
        
    # Access
    #

    def index(self):
        return self.index_
    
    # Position
    def row(self):
        return self.row_
    def line(self):
        return self.line_
    def squareID(self):
        return self.squareID_

    #
    # Change index
    #

    # +=
    #
    def __iadd__(self, inc):
        self.index_ += inc
        # Reach the end of the matrix ?
        if self.index_ > self.INDEX_MAX:
            if True == self.gameMode_ :
                raise reachedEndOfList
            else:
                if self.index_ > (1+self.INDEX_MAX):
                    raise IndexError

        self._whereAmI()
        return self

    # -=
    #
    def __isub__(self, dec):
        self.index_ -= dec
        if self.index_ < self.INDEX_MIN:
            raise IndexError

        self._whereAmI()
        return self

    # Change "row"
    #
    def decRow(self, dec = 1):
        row = self.row_ - dec
        if row < 0:
            self.index_ = (1 + self.line_ ) * self.ROW_COUNT + row 
        else:
            self.index_ -= dec
        self._whereAmI()

    def incRow(self, inc = 1):
        row = self.row_ + inc
        if row >= self.ROW_COUNT:
            self.index_ = (self.line_ - 1) * self.ROW_COUNT + row 
        else:
            self.index_ += inc
        self._whereAmI()
    
    # Change "line"
    #
    def decLine(self, dec = 1):
        self.index_ -= self.ROW_COUNT * dec
        if self.index_ < self.INDEX_MIN:
            self.index_ = self.row_ + (self.ROW_COUNT - 1) * self.ROW_COUNT
        self._whereAmI()

    def incLine(self, inc = 1):
        self.index_ += self.ROW_COUNT * inc
        if self.index_ > self.INDEX_MAX:
            self.index_ = self.row_
        self._whereAmI()

    #
    # Change the value
    #

    def incValue(self, value):
        newVal = value + 1
        return (self.VALUE_MIN - 1) if newVal > self.VALUE_MAX else newVal

    def decValue(self, value):  
        newVal = value - 1
        return self.VALUE_MAX if newVal < (self.VALUE_MIN - 1) else newVal

    #
    #   internal methods
    #

    # Updating coordinates
    #
    def _whereAmI(self, all = True):
        
        if True == all:
            # V. math
            self.line_ = math.floor(self.index_ / self.ROW_COUNT)
            self.row_ = self.index_ - self.ROW_COUNT * self.line_
        
        # Small square ID
        self.squareID_ = 3 * math.floor(self.line_ / 3) + math.floor(self.row_ / 3)

    # check position
    #
    def _setInRange(self, value):
        return 0 if value < 0 else (self.ROW_COUNT - 1) if value >= self.ROW_COUNT else value
        #return value

# EOF