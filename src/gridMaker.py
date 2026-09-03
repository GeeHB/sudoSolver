# coding=UTF-8
#
#   File        :   gridMaker.py
#
#   Author      :   GeeHB
#
#   Description :   Creation of a grid
#

import random

from options import options as opts
from pointer import GRID_SIZE, INDEX_MAX, INDEX_MIN, VALUE_MAX, VALUE_MIN
from pointer import pointer as position
from sudoku import sudoku


#   gridMaker : Creation of a new sudoku grid
#
class gridMaker:

    # Construction
    def __init__(self, grid :sudoku | None = None, complexity:int = opts.COMPLEXITY_EASY):
        random.seed()
        self.complexity_ :int = complexity
        self.grid_ : sudoku | None = grid if grid is not None else sudoku(initOutputs = False);

    # Create a new full grid
    def newGrid(self):
        if self.grid_ is not None:
            # Step 1 - Start from a complete (new) grid
            self.grid_.clear()
            _ = self.grid_.resolve()

            # Step 2 : shuffle elements
            self._shuffleValues()

            # Step 3 : rearrange columns
            self._shuffleColumns()

            # Step 4: rearrange rows
            self._shuffleRows();

            # Step 5 : rearrange block of columns
            self._shuffleColumnBlocks();

            # Step 6 : rearrange block of lines
            self._shuffleRowBlocks();

            # Step 7 : all elements are "original"
            for index in range(GRID_SIZE):
                self.grid_.elements_[index].setOriginal();

    # Remove elements according to complexity
    #
    def removeElements(self, complexity:int = opts.COMPLEXITY_EASY):
        if self.grid_ is not None:
            if complexity != opts.COMPLEXITY_EASY:
                self.complexity_ = complexity

            clues = GRID_SIZE

            while clues > complexity :
                index = random.randint(0, GRID_SIZE - 1)

                if not self.grid_.elements_[index].isEmpty() :
                    _ = self.grid_.elements_[index].empty()
                    clues-=1

            return clues

        return 0

    # _shuffleValues() : randomly shuffle elements' values
    #
    def _shuffleValues(self):
        for first in range(VALUE_MIN, VALUE_MAX + 1):
            self._swapValues(first, random.randint(1, VALUE_MAX))

    # _shuffleColumns() : randomly shuffle 2 columns in the same block
    #
    def _shuffleColumns(self):
        colOff = 0
        for _ in range(3):
            for colID in range(3):
                self._swapColumns(colID + colOff, colOff + random.randint(0, 2))

            colOff+=3;  # Next block

    # _shuffleRows() : randomly shuffle 2 rows in the same block
    #
    def _shuffleRows(self):
        rowOff =0
        for _ in range(3):
            for rowID in range(3):
                self._swapRows(rowID + rowOff, random.randint(0, 2) + rowOff);

            rowOff+=3;  # Next block

    # _shuffleColumnBlocks() : randomly shuffle 2 blocks of 3 columns
    #
    def _shuffleColumnBlocks(self):
        for blockID in range(3):
            self._swapColumnBlocks(blockID, random.randint(0, 2))

    # _shuffleRowBlocks() : randomly shuffle 2 blocks of 3 rows
    #
    def _shuffleRowBlocks(self):
        for blockID in range(3):
            self._swapRowBlocks(blockID, random.randint(0, 2))

    # _swapValues() : Swap 2 values in the whole grid
    #
    #  @first : value to replace by @second
    #  @second : value to replace by @first
    #
    def _swapValues(self, first:int, second:int):
        if self.grid_ is not None and first != second:
            for index in range(INDEX_MIN, INDEX_MAX):
                value = self.grid_.elements_[index].num
                if value == first:
                    self.grid_.elements_[index].num = second
                else:
                    if self.grid_.elements_[index].num == second:
                        self.grid_.elements_[index].num = first

    # _swapColumns() : Swap the elements of 2 columns
    #
    #  @fCol : col ID to swap with @sCol
    #  @sCol : col ID to swap with @fcol
    #
    def _swapColumns(self, fCol:int, sCol:int):
        if self.grid_ is not None and fCol != sCol:
            first = position()
            second = position()

            first.moveTo(0, fCol);
            second.moveTo(0, sCol);

            for _ in range(VALUE_MAX):
                oValue : int | None = self.grid_.elements_[first.index()].num;
                self.grid_.elements_[first.index()].num = self.grid_.elements_[second.index()].num
                self.grid_.elements_[second.index()].num = oValue

                # Next line
                first.incLine();
                second.incLine();

    # _swapRows() : Swap the elements of 2 rows
    #
    #  @fRow : row ID to swap with @sRow
    #  @sRow : row ID to swap with @fRow
    #
    def _swapRows(self, fRow:int, sRow:int):
        if self.grid_ is not None and fRow != sRow:
            first = position()
            second = position()

            first.moveTo(fRow, 0);
            second.moveTo(sRow, 0);

            for _ in range(VALUE_MAX):
                oValue = self.grid_.elements_[first.index()].num
                self.grid_.elements_[first.index()].num = self.grid_.elements_[second.index()].num
                self.grid_.elements_[second.index()].num = oValue

                # Next row
                first.incRow();
                second.incRow();

    # _swapColumnBlocks() : Swap blocks of 3 contiguous columns
    #
    def _swapColumnBlocks(self, fColBlock:int, sColBlock:int):
        if fColBlock != sColBlock:
             for colID in range(3):
                self._swapColumns(fColBlock * 3 + colID, sColBlock * 3 + colID);

    # _swapRowBlocks() : Swap blocks of 3 contiguous rows
    #
    def _swapRowBlocks(self, fRowBlock:int, sRowBlock:int):
        if fRowBlock != sRowBlock:
             for rowID in range(3):
                self._swapRows(fRowBlock * 3 + rowID, sRowBlock * 3 + rowID);
# EOF
