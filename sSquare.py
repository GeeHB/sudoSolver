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

from ownExceptions import reachedEndOfList
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

    LINE_COUNT = 3
    ROW_COUNT = 3

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

    # Get index form positionnal index (of an element)
    #
    def IdFromIndex(self, index):
        self.Id_ = index
    
    # Access
    #

    def Id(self):
        return self.Id_
    
    # Indexes by line
    #
    #   returns a 3x3 matrix : line[0] / line[1] / line[2]
    #
    def indexesByLine(self):

        matrix = []

        # Start index
        index = SQUARES_INDEXES[self.Id_]      
        for _ in range (self.LINE_COUNT):
            line = []    
            for row in range(self.ROW_COUNT):
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
        for rowID in range (self.LINE_COUNT):
            line = []    
            for lineID in range(self.ROW_COUNT):
                line.append(index)
                index += element.ROW_COUNT

            matrix.append(line)
            index = SQUARES_INDEXES[self.Id_] + rowID

        return matrix

    # Is the value "in" the square ?
    def inMe(self, elements, value):
        
        # All my positions
        positions = self.indexesByLine()

        # Check all the positions
        for line in range (sSquare.LINE_COUNT):
            for row in range(sSquare.ROW_COUNT):
                if value == elements[positions[line][row]].value():
                    # This value is already in the square
                    return True
        
        # No (this value is not in this small square)
        return False

# EOF