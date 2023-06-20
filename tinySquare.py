# coding=UTF-8
#
#   File        :   tinySquare.py
#
#   Author      :   GeeHB
#
#   Description :   tinySquare object 
#

from pointer import pointer

# Top-left index of tiny-squares
#
TINY_SQUARES_INDEXES = [0, 3, 6, 27, 30, 33, 54, 57, 60]

#
# tinySquare object
#
#   A tiny-square is one of the 9 3x3 matrix composing the whole grid
#
class tinySquare(object):

    # Dimensions
    TINY_LINE_COUNT = 3
    TINY_ROW_COUNT = 3

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
        if type(other) is tinySquare:
            self.Id_ = other.Id_
            self.topLine_ = other.topLine_
            self.topRow_ = other.topRow_

    # Get index from positionnal index (of an element)
    #
    def IdFromIndex(self, index):
        if type(index) is int:
            if index < 0 or index >= (self.TINY_LINE_COUNT * self.TINY_ROW_COUNT):
                raise IndexError

            self.Id_ = index

            # "top" values
            position = pointer(index = TINY_SQUARES_INDEXES[index])
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
    def indexes(self):

        ids = []

        # Start index
        index = TINY_SQUARES_INDEXES[self.Id_]      
        for _ in range (self.TINY_LINE_COUNT):
            line = []    
            for row in range(self.TINY_ROW_COUNT):
                line.append(index + row)    # Add the index to the line
            
            ids.append(line)                # Add the line to the matrix
            index+=pointer.ROW_COUNT

        # Finish !!!
        return ids
    
    # Search for the position of the value "in" the square
    #
    #   returns the tuple (line, row) if found or (None, None)
    #
    def findValue(self, elements, value):
        
        # All my positions
        positions = self.indexes()

        # Check all the positions
        for line in range (tinySquare.TINY_LINE_COUNT):
            for row in range(tinySquare.TINY_ROW_COUNT):
                if value == elements[positions[line][row]].value():
                    # This value is in the square
                    return (line, row)
        
        # No, this value is not in this square
        return (None, None)

    # Is the value "in" the square ?
    #
    #   Check wether the value is already present in the current tiny-square   
    #
    #   return a boolean - True if found
    #
    def inMe(self, elements, value):
        return False if None == self.findValue(elements, value)[0] else True

# EOF