# coding=UTF-8
#
#   File        :   sArray.py
#
#   Author      :   GeeHB
#
#   Description :   A sudoku array
#

import copy
import math
import os
import random
import time
from typing import override

from element import element
from options import (
    FILE_COMMENTS,
    FILE_EXPORT_EXTENSION,
    FILE_VALUE_SEPARATOR,
    arrayComplexity,
)
from ownExceptions import reachedEndOfList, sudokuError
from pointer import (
   ARRAY_SIZE,
   INDEX_MAX,
   INDEX_MIN,
   LINE_COUNT,
   ROW_COUNT,
   VALUE_MAX,
   VALUE_MIN,
   pointer,
)
from tinySquare import tinySquare


#   sArray : A sudoku array
#
class sArray:
    # Construction
    def __init__(self):
        self.fileName_ : str | None = None
        self.attempts_:int = 0
        self.start_:float = 0.0  # Resolution start-time
        self.elements_ : list[element] = []
        self.complexity_ : int = arrayComplexity.COMPLEXITY_EMPTY

        random.seed()

    # Filename
    @property
    def filename(self)->str|None:
        return self.fileName_

    # complexity
    @property
    def complexity(self)->int:
        return self.complexity_
    @complexity.setter
    def complexity(self, newVal : int | None):
        if newVal is not None:
            self.complexity_ = newVal

    # Convert current array to a printable string
    #
    @override
    def __str__(self)->str:
        output : str = ""  # to stop warnings !!!!
        if len(self.elements_) == ARRAY_SIZE:
            position : pointer = pointer(gameMode=False)
            for _ in range(LINE_COUNT):
                output += "\n"
                for _ in range(ROW_COUNT):
                    currentElement = self.elements_[position.index()]
                    output += f" {' ' if currentElement.isEmpty() else str(currentElement.num)} "
                    position += 1
            output += "\n"

        return output

    # Create an empty array or clear currrent one
    #
    def empty(self):
        if len(self.elements_) > 0:
            for index in range(ARRAY_SIZE):
                self.elements_[index].empty(deep = True)
        else:
            for _ in range(ARRAY_SIZE):
                self.elements_.append(element())

    # Create a new full array
    #
    def new(self, compl : int | None):
        self.empty()

        if compl is None or compl == arrayComplexity.COMPLEXITY_EMPTY:
            self.complexity_ = arrayComplexity.COMPLEXITY_EMPTY
            return  # returns an empty array

        self.complexity = compl

        # Step 1 - Start from a complete (new) grid
        _ = self.resolve()

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
        for index in range(ARRAY_SIZE):
            self.elements_[index].setOriginal();

        # Step 8 : Remove elements according to complexite
        self._removeElements()

    # Return to the original state
    #
    def revert(self):
        for el in self.elements_:
            if not el.isOriginal():
                el.empty(deep = False)

    # Read a grid'file
    #
    def load(self, fileName : str | None, mustExist : bool, showFileName:bool = True):
        if fileName is None or 0 == len(fileName):
            # ???
            raise sudokuError("No valid file name")

        if os.path.isdir(fileName):
            raise sudokuError(f"{fileName} is not a valid file")

        self.fileName_ = fileName

        # Open and read the file
        #
        try:
            with open(fileName) as file:
                pt = pointer(gameMode=False)

                # Read the lines
                for line in file:
                    # Not a comment !
                    if line[0] != FILE_COMMENTS:
                        # remove EOL
                        if line[len(line) - 1] == "\n":
                            line = line[: len(line) - 1]

                        values = line.split(FILE_VALUE_SEPARATOR)

                        if not ROW_COUNT == len(values):
                            raise sudokuError(
                                f"Invalid format for line n° {(pt.line() + 1)!r} - {len(values)!r} values"
                            )

                        for val in values:
                            self._setAt(pt, val)

                            # Next value
                            pt += 1
        except FileNotFoundError:
            if True == mustExist:
                raise sudokuError(f"The file '{fileName}' doesn't exist")
            else:
                print(f"New file : '{fileName}'")

    # Save the file
    #
    #   return the name of the saved file or None if an error occured
    #
    def save(self, genName:bool = False, comments:list[str] | None = None, newFileName:str | None = None):

        if self.fileName_ is None:
            return None

        # A new name ?
        if newFileName is not None:
            self.fileName_ = newFileName
            # self.outputs_.setGridName(newFileName, create=True)

        fileName = self.fileName_
        if genName:
            fileName += FILE_EXPORT_EXTENSION
        try:
            with open(fileName, "w") as file:
                # a few comments ?
                if comments and len(comments):
                    for comment in comments:
                        line = FILE_COMMENTS
                        line += " "
                        line += comment
                        line += "\n"
                        file.write(line)

                # File content
                pt = pointer(gameMode=False)
                for lIndex in range(LINE_COUNT):
                    line = ""
                    for _ in range(ROW_COUNT):
                        el = self.elements_[pt.index()]
                        line += str(0 if el.isEmpty() else el.num)
                        line += FILE_VALUE_SEPARATOR
                        pt += 1

                    # add separator
                    line = line[: len(line) - 1]
                    if lIndex < (LINE_COUNT - 1):
                        line += "\n"

                    file.write(line)

            # file.close()
            return fileName
        except FileNotFoundError:
            # raise sudokuError(f"io error while writing the file '{fileName}'")
            print(f"io error while writing the file '{fileName}'")
            return None

    #
    # Array creation
    #

    # Remove elements according to complexity
    #
    def _removeElements(self):
        clues = ARRAY_SIZE
        while clues > self.complexity :
            index = random.randint(0, ARRAY_SIZE - 1)

            if not self.elements_[index].isEmpty() :
                _ = self.elements_[index].empty(deep = False)
                clues-=1

        return clues


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

    # _swapValues() : Swap 2 values in the whole array
    #
    #  @first : value to replace by @second
    #  @second : value to replace by @first
    #
    def _swapValues(self, first:int, second:int):
        if first != second:
            for index in range(INDEX_MIN, INDEX_MAX):
                value = self.elements_[index].num
                if value == first:
                    self.elements_[index].num = second
                else:
                    if self.elements_[index].num == second:
                        self.elements_[index].num = first

    # _swapColumns() : Swap the elements of 2 columns
    #
    #  @fCol : col ID to swap with @sCol
    #  @sCol : col ID to swap with @fcol
    #
    def _swapColumns(self, fCol:int, sCol:int):
        if fCol != sCol:
            first : pointer = pointer()
            second : pointer = pointer()

            first.moveTo(0, fCol);
            second.moveTo(0, sCol);

            for _ in range(VALUE_MAX):
                oValue : int | None = self.elements_[first.index()].num;
                self.elements_[first.index()].num = self.elements_[second.index()].num
                self.elements_[second.index()].num = oValue

                # Next line
                first.incLine();
                second.incLine();

    # _swapRows() : Swap the elements of 2 rows
    #
    #  @fRow : row ID to swap with @sRow
    #  @sRow : row ID to swap with @fRow
    #
    def _swapRows(self, fRow:int, sRow:int):
        if fRow != sRow:
            first : pointer = pointer()
            second : pointer = pointer()

            first.moveTo(fRow, 0);
            second.moveTo(sRow, 0);

            for _ in range(VALUE_MAX):
                oValue = self.elements_[first.index()].num
                self.elements_[first.index()].num = self.elements_[second.index()].num
                self.elements_[second.index()].num = oValue

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

    #
    #  Resolution
    #
    #

    #
    # Solve the grid (internal method without exceptions handling)
    #

    # Single Threaded mode (default)
    #
    def resolve(self)->tuple[bool, bool, int, float]:
        escaped = False
        found = True  # We assume we'll find a solution !

        # for stats
        self.attempts_ = 0
        self.start_ = time.time()
        endTime = 0

        # Let's go
        try:
            self._resolveSingleThreaded()
        except reachedEndOfList:
            # Found a solution !!!
            endTime = time.time() - self.start_
        except IndexError:
            # No solution found
            found = False
        # except:
        # escaped = True

        # Finished (anyway)
        return (found, escaped, self.attempts_, endTime)

    # Single Threaded mode (default)
    #
    def _resolveSingleThreaded(self):
        candidate : int = 0
        position : pointer = pointer(gameMode=True)
        position = self._findFirstEmptyPos(position)

        # All the elements "before" the current position are set with possible/allowed values
        # we'll try to put the "candidate" value at the current position
        while True:
            candidate += 1
            if candidate > VALUE_MAX:
                # No possible value found at this position
                # we'll have to go backward, to the last value setted
                position = self._previousPos(position)

                # candidate value = prev. value (incremented at next occurence)
                candidate = self.elements_[position.index()].empty(deep = False)
            else:
                # Try to put the "candidate" value at current position
                #
                if True == self._checkValue(position, candidate):
                    # possible !!!
                    self.attempts_ += 1

                    self.elements_[position.index()].setValue(candidate)

                    # Go to the next "empty" position
                    position = self._findFirstEmptyPos(position)

                    # At the next pos., we alawyas try the lowest possible value
                    candidate = 0

    # Can we put the value at the current position ?
    #
    def _checkValue(self, position:pointer, value:int)->bool:
        return (
            self._checkLine(position, value)
            and self._checkRow(position, value)
            and self._checkTinySquare(position, value)
        )

    #   => in the line ?
    def _checkLine(self, position:pointer, value:int)->bool:
        idFirst = position.line() * ROW_COUNT
        for tIndex in range(ROW_COUNT):
            if self.elements_[tIndex + idFirst].num == value:
                return False
        # yes
        return True

    #  => in the row ?
    def _checkRow(self, position:pointer, value:int)->bool:
        idFirst = position.row()
        for tIndex in range(LINE_COUNT):
            if self.elements_[tIndex * ROW_COUNT + idFirst].num == value:
                return False
        # yes
        return True

    #  => in the tiny-square ?
    def _checkTinySquare(self, position:pointer, value:int)->bool:
        # Search in my tiny-square
        mySquare : tinySquare = tinySquare(position.squareID())
        return False == mySquare.inMe(self.elements_, value)

    # (try to) set a value at current position
    def _setAt(self, position : pointer, val:str, warn:bool=True) -> bool:
        value = int(val)

        # in [0,9] ?
        value = int(val)
        if value < 0 or value > 9:
            if warn:
                raise sudokuError(
                    f"Value Error : {value} is not in the valid range in ({(position.line() + 1)!r},{(position.row() + 1)!r})"
                )
            return False

        if value > 0:
            # Check the line
            if False == self._checkLine(position, value):
                if warn:
                    raise sudokuError(
                        f"Line value error : value {value} can't be set in ({(position.line() + 1)!r},{(position.row() + 1)!r})"
                    )
                return False

            # Check the row
            if False == self._checkRow(position, value):
                if warn:
                    raise sudokuError(
                        f"Row value error : value {value} can't be set in ({(position.line() + 1)!r},{(position.row() + 1)!r})"
                    )
                return False

            # Check the tiny-square
            if False == self._checkTinySquare(position, value):
                if warn:
                    raise sudokuError(
                        f"Square value error : value {value} can't be set in ({(position.line() + 1)!r},{(position.row() + 1)!r})"
                    )
                return False

            # Set the value
            self.elements_[position.line() * ROW_COUNT + position.row()].setValue(
                value, element.STATUS_ORIGINAL
            )
            return True

        return False  # Value not set

    # Find the next empty pos.
    #
    #   Returns a pointer to the found position
    #   An exception reachedEndOfList is raised when the grid is full (the game is over and a solution has been found)
    #
    def _findFirstEmptyPos(self, start:pointer)->pointer:
        newPos : pointer = copy.deepcopy(start)
        while not self.elements_[newPos.index()].isEmpty():
            newPos += 1

        # Done
        return newPos

    # Returns to the previous position
    #
    #   Returns a pointer to the found position
    #   An IndexError exception is raised when the pointer is out of the grid (index -1)
    #   No solution for the grid
    #
    def _previousPos(self, current:pointer)->pointer:
        newPos : pointer = copy.deepcopy(current)
        self.elements_[newPos.index()].empty(deep = False)
        newPos -= 1

        # while self.elements_[newPos.index()].isOriginal():

        # Don't touch "Original" nor "Obvious" values
        while not self.elements_[newPos.index()].isChangeable():
            newPos -= 1

        # Ok
        return newPos

    # Find the next possible value for an element (greater than the current one)
    #
    def _findNextValue(self, position : pointer, val : int)->int:
        nextVal : int = position.incValue(val)
        while val != nextVal:
            if self._checkValue(position, nextVal):
                return nextVal
            # try the next value
            nextVal = position.incValue(nextVal)

        return nextVal

    # Find the lowest possible value for an element
    #
    def _findPreviousValue(self, position : pointer, val : int)->int:
        nextVal : int = position.decValue(val)
        while val != nextVal:
            if self._checkValue(position, nextVal):
                # found it
                return nextVal

            # may be the prev ?
            nextVal = position.decValue(nextVal)

        # No other possible value (than the initial)
        return nextVal

    #
    #   Obvious values
    #

    # Find all the obvious values
    #
    #   return a tuple (#obvious values, duration in s.)
    #
    def findObviousValues(self)->tuple[int, float]:
        found : int = 0
        start : float = time.time()
        values = 1
        while 0 < values:
            values = self._findObviousValues()
            found += values

        # Find a solution !!!
        return found, time.time() - start

    # Search and set all the possible obvious values in the grid
    #   returns the # of values found (and set)
    #
    def _findObviousValues(self)->int:
        found : int = 0
        position : pointer = pointer()

        for _ in range(INDEX_MAX):
            if self.elements_[position.index()].isEmpty():
                # Try to set a single value at this empty place
                value = self._checkObviousValue(position)

                if value is not None:
                    # One more obvious value !!!!
                    self.elements_[position.index()].setValue(
                        value, element.STATUS_OBVIOUS
                    )
                    #print(self.elements_[position.index()])
                    found += 1
            else:
                value = self.elements_[position.index()].num

                if value is not None :
                    # Can we put this value on another line ?
                    found += self._setObviousValueInLines(position, value)

                    # ... or/and put it in another col ?
                    found += self._setObviousValueInRows(position, value)

            # Next pos.
            position += 1

        # End of search loop
        return found

    # Is there an obvious value for the given position ?
    #
    #      returns the value (if just one possible) or None
    #
    def _checkObviousValue(self, position:pointer)-> int | None:
        value : int | None = None
        for test in range(VALUE_MIN, VALUE_MAX + 1):
            if self._checkValue(position, test):
                # This value can be used
                if value:
                    # already a possible value at this pos.
                    # => not a unique value
                    return None
                value = test

        # Finish
        return value

    # Try to put the value in another line
    #
    #   return the count (0 or 1) of value set
    #
    def _setObviousValueInLines(self, position:pointer, value:int)->int:
        # "little" squares IDs for this line
        modID : int = position.squareID() % 3
        if 0 == modID:
            # At the left pos
            firstSquare = tinySquare(position.squareID() + 1)
            secondSquare = tinySquare(position.squareID() + 2)
        else:
            if 1 == modID:
                # centered
                firstSquare = tinySquare(position.squareID() - 1)
                secondSquare = tinySquare(position.squareID() + 1)
            else:
                # on the right
                firstSquare = tinySquare(position.squareID() - 2)
                secondSquare = tinySquare(position.squareID() - 1)

        # Is the value already in theses squares ?
        firstPos : tuple[int | None ,int | None] = firstSquare.findValue(self.elements_, value)
        secondPos : tuple[int | None, int | None] = secondSquare.findValue(self.elements_, value)

        # None of them or both of them
        if (firstPos[0] is None and secondPos[0] is None) or (
            not firstPos[0] is None and not secondPos[0] is None
        ):
            return 0

        # Just one square misses the value => we'll try to put this value in the correct line
        #
        #   The sum of the 3 lineID is a consts and we know 2 oh them
        #
        candidateLine : int = 0
        candidate : tinySquare = firstSquare
        if firstPos[0] is None:
            if secondPos[0] is not None :
                candidateLine = (
                    2 * (firstSquare.topLine() + 1) - secondPos[0] - position.line() + 1
                )
        else:
            candidate = secondSquare
            candidateLine = (
                2 * (secondSquare.topLine() + 1) - firstPos[0] - position.line() + 1
            )

        # Try to put the value ...
        #
        foundPos = None
        pos = pointer(index=0)
        pos.moveTo(candidateLine, candidate.topRow())

        try:
            for _ in range(tinySquare.TINY_ROW_COUNT):
                if self.elements_[pos.index()].isEmpty() and self._checkValue(
                    pos, value
                ):
                    if None != foundPos:
                        # Already a candiate => not obvious
                        return 0
                    foundPos = copy.deepcopy(pos)  # // copy constructor

                # Next row
                pos += 1
        except (
            reachedEndOfList
        ):  # Might go out of range and raise reachedEndOfList exception
            pass

        # Did we find a position ?
        if foundPos is not None:
            # Yes !!!
            self.elements_[foundPos.index()].setValue(value, element.STATUS_OBVIOUS)
            #print(f"Line - Position : {foundPos} - {self.elements_[foundPos.index()]}")
            return 1

        # No ...
        return 0

    # Try to put the value in another row
    #
    #   return the count (0 or 1) of value set
    #
    def _setObviousValueInRows(self, position:pointer, value:int) -> int:
        # "little" squares IDs for this line
        modID = math.floor(position.squareID() / 3)
        if 0 == modID:
            # At the top pos
            firstSquare = tinySquare(position.squareID() + tinySquare.TINY_ROW_COUNT)
            secondSquare = tinySquare(
                position.squareID() + 2 * tinySquare.TINY_ROW_COUNT
            )
        else:
            if 1 == modID:
                # centered
                firstSquare = tinySquare(
                    position.squareID() - tinySquare.TINY_ROW_COUNT
                )
                secondSquare = tinySquare(
                    position.squareID() + tinySquare.TINY_ROW_COUNT
                )
            else:
                # on the bottom
                firstSquare = tinySquare(
                    position.squareID() - 2 * tinySquare.TINY_ROW_COUNT
                )
                secondSquare = tinySquare(
                    position.squareID() - 1 * tinySquare.TINY_ROW_COUNT
                )

        # Is the value already in theses squares ?
        firstPos = firstSquare.findValue(self.elements_, value)
        secondPos = secondSquare.findValue(self.elements_, value)

        # None of them or both of them
        if (firstPos[0] is None and secondPos[0] is None) or (
            not firstPos[0] is None and not secondPos[0] is None
        ):
            return 0

        # Just one square misses the value => we'll try to put this value in the correct line
        #
        #   The sum of the 3 lineID is a consts and we know 2 of them
        #
        candidateRow : int = 0
        candidate : tinySquare = firstSquare
        if firstPos[0] is None:
            if secondPos[1] is not None:
                candidateRow = (
                    2 * (firstSquare.topRow() + 1) - secondPos[1] - position.row() + 1
                )
        else:
            if firstPos[1] is not None:
                candidate = secondSquare
                candidateRow = (
                    2 * (secondSquare.topRow() + 1) - firstPos[1] - position.row() + 1
                )

        # Try to put the value ...
        #
        foundPos = None
        pos = pointer(index=0)
        pos.moveTo(candidate.topLine(), candidateRow)

        try:
            for _ in range(tinySquare.TINY_LINE_COUNT):
                if self.elements_[pos.index()].isEmpty() and self._checkValue(
                    pos, value
                ):
                    if None != foundPos:
                        # Already a candiate => not obvious
                        return 0

                    foundPos = copy.deepcopy(pos)

                # Next line
                pos += ROW_COUNT  # Might go out of range and raise reachedEndOfList exception
        except reachedEndOfList:
            pass

        # Did we find a valid position ?
        if foundPos is not None:
            # Yes !!!
            self.elements_[foundPos.index()].setValue(value, element.STATUS_OBVIOUS)
            #print(f"Row - Position : {foundPos} - {self.elements_[foundPos.index()]}")
            return 1

        # No ...
        return 0

# EOF
