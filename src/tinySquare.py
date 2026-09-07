# coding=UTF-8
#
#   File        :   tinySquare.py
#
#   Author      :   GeeHB
#
#   Description :   tinySquare object
#
from element import element
from pointer import ROW_COUNT, pointer


#
# tinySquare object
#
#   A tiny-square is one of the 9 3x3 matrix composing the whole grid
#
class tinySquare:

    # Dimensions
    TINY_LINE_COUNT:int = 3
    TINY_ROW_COUNT:int = 3

    # Construction
    #
    def __init__(self, index:int | None = None):
        if index is not None:
            self.Id_ : int = self.IdFromIndex(index)
        self.topLine_:int = 0
        self.topRow_:int = 0

        # Top-left index of tiny-squares
        #
        self.SquaresIndexes : list[int] = [0, 3, 6, 27, 30, 33, 54, 57, 60]

    # Get index from positionnal index (of an element)
    #
    def IdFromIndex(self, id:int)->int:

        if id < 0 or id >= (self.TINY_LINE_COUNT * self.TINY_ROW_COUNT):
            raise IndexError

        # "top" values
        position = pointer(index = self.SquaresIndexes[id])
        self.topLine_ = position.line_
        self.topRow_ = position.row_

        return id

    # Access
    #
    def Id(self)->int:
        return self.Id_

    # Top indexes
    def topLine(self)->int:
        return self.topLine_

    def topRow(self)->int:
        return self.topRow_

    # Indexes by line
    #
    #   returns a 3x3 matrix : line[0] / line[1] / line[2]
    #
    def indexes(self):
        ids :list[list[int]]= []

        # Start index
        index = self.SquaresIndexes[self.Id_]
        for _ in range (self.TINY_LINE_COUNT):
            line : list[int]= []
            for row in range(self.TINY_ROW_COUNT):
                line.append(index + row)    # Add the index to the line

            ids.append(line)                # Add the line to the matrix
            index+=ROW_COUNT

        # Finish !!!
        return ids

    # Search for the position of the value "in" the square
    #
    #   returns the tuple (line, row) if found or (None, None)
    #
    def findValue(self, elements:list[element], value:int)->(tuple[int | None,int | None]):
        # All my positions
        positions:list[list[int]] = self.indexes()

        # Check all the positions
        for line in range (tinySquare.TINY_LINE_COUNT):
            for row in range(tinySquare.TINY_ROW_COUNT):
                if value == elements[positions[line][row]].num:
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
    def inMe(self, elements:list[element], value:int)->bool:
        return not bool(self.findValue(elements, value)[0] == -1)

# EOF
