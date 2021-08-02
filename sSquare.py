# coding=UTF-8
#
#   File     :   sSquare.py
#
#   Author      :   JHB
#
#   Description :   "sSquare" object 
#
#   Version     :   1.2.4
#
#   Date        :   2021-07-21
#

from pointer import pointer
from element import element

# Top-left index of "small" squares
#
SQUARES_INDEXES = [0, 3, 6, 27, 30, 33, 54, 57, 60]

#
# sSquare object
#
#   A "small" square is one of the 9 3x3 matrix composing the whole grid
#
class sSquare(object):

    S_LINE_COUNT = 3
    S_ROW_COUNT = 3

    MAX_ID = 8

    # Construction
    #
    def __init__(self, index = None, other = None):
        # Copy ?
        #
        if not None == other:
            self.set(other)
        else:
            self.IdFromIndex(index)

    # Copy constrcutor
    #
    def set(self, other):
        if type(other) is sSquare:
            self.Id_ = other.Id_
            self.topLine_ = other.topLine_
            self.topRow_ = other.topRow_

    # Get index from positionnal index (of an element)
    #
    def IdFromIndex(self, index):
        if type(index) is int:
            if index < 0 or index > self.MAX_ID:
                raise IndexError

            self.Id_ = index

            # "top" values
            position = pointer(index = SQUARES_INDEXES[index])
            self.topLine_ = position.line_
            self.topRow_ = position.row_

    # Access
    #
    def Id(self):
        return self.Id_
    
    # Top indexes
    def topLine(self):
        return self.topLine_
        
    def topRow(self):
        return self.topRow_
    
    # Indexes by line
    #
    #   returns a 3x3 matrix : line[0] / line[1] / line[2]
    #
    def indexesByLine(self):

        matrix = []

        # Start index
        index = SQUARES_INDEXES[self.Id_]      
        for _ in range (self.S_LINE_COUNT):
            line = []    
            for row in range(self.S_ROW_COUNT):
                line.append(index + row)
            
            matrix.append(line)
            index+=pointer.ROW_COUNT

        return matrix
    
    # Indexes by row
    #
    #   returns a 3x3 matrix : row[0] / row[1] / row[2]
    #
    def indexesByRow(self):
        matrix = []

        # Start index
        index = SQUARES_INDEXES[self.Id_]      
        for rowID in range (self.S_LINE_COUNT):
            line = []    
            for lineID in range(self.S_ROW_COUNT):
                line.append(index)
                index += element.ROW_COUNT

            matrix.append(line)
            index = SQUARES_INDEXES[self.Id_] + rowID

        return matrix

    # Search for the position of the value "in" the square ?
    #
    #   returns the tuple (line, row) if found or (None, None)
    #
    def findValue(self, elements, value):
        
        # All my positions
        positions = self.indexesByLine()

        # Check all the positions
        for line in range (sSquare.S_LINE_COUNT):
            for row in range(sSquare.S_ROW_COUNT):
                if value == elements[positions[line][row]].value():
                    # This value is in the square
                    return (line, row)
        
        # No (this value is not in this small square)
        return (None, None)

    # Is the value "in" the square ?
    #
    #   Check wether the value is in the current small square   
    #
    #   return a boolean - True if found
    #
    def inMe(self, elements, value):
        rets = self.findValue(elements, value)
        return False if None == rets[0] else True

# EOF