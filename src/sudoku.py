# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   sudoku object
#                       - load / save / detect from OCR
#                       -  edit and/or resolve of a sudoku's grid
#

import copy
import math
import os
import sys
import time
from typing import override

from element import element
from options import FILE_EXPORT_EXTENSION, options, stats
from options import options as opts
from ownExceptions import reachedEndOfList, sudokuError
from pointer import (
    ARRAY_SIZE,
    INDEX_MAX,
    LINE_COUNT,
    ROW_COUNT,
    VALUE_MAX,
    VALUE_MIN,
    pointer,
)
from pygameOutputs import pygameOutputs
from pygameThreadedOutputs import pygameThreadedOutputs
from sharedTools import statusbits
from tinySquare import tinySquare


#   sudoku : Edition and/or resolution of a single sudoku grid
#
class sudoku:


    # Construction
    #
    def __init__(self, progress:int = options.PROGRESS_NONE):

        self.gridFileName_ : str | None = None
        self.outputs_ = None

        self.attempts_:int = 0
        self.start_:float = 0.0  # Resolution start-time
        self.editStatus_:statusbits.statusBits = statusbits.statusBits(self.EDIT_CONTINUE)

        self.elements_ : list[element] = []
        self.OSInfos_ = {}  # Informations about the OS and the Window manager

        # Show progression details ?
        self.progressMode_:int = progress

        # Try with PYGame
        try:
            self._createOutputsGUI()
        except ModuleNotFoundError:
            print("PYGame isn't installed. Try pip install pygame")
            sys.exit()
        except sudokuError as e:
            print(e)

        if self.outputs_ is None:
            sys.exit()

        # Ready ?
        while not self.outputs_.isReady():
            time.sleep(0.1)

        #print("GUI Ok")

        # Create the grid
        self._emptyGrid()
        #print("Empty GRID")

    # Destruction
    #
    def __del__(self):
        # Delete display manager
        if self.outputs_ is not None:
            self.outputs_ = None

    # Empty the grid
    #
    def clear(self):
        self._emptyGrid()

    # Create an empty grid
    #
    def _emptyGrid(self):
        if len(self.elements_) > 0:
            self.elements_.clear()

        for _ in range(ARRAY_SIZE):
            self.elements_.append(element())

    # Progress mode (ie. display progression ?)
    #
    def progressMode(self) -> int:
        return self.progressMode_

    # Filename (of the source grid)
    #
    def fileName(self)->str | None:
        return self.gridFileName_

    # Access
    #
    def outputs(self):
        return self.outputs_

    def grid(self):
        return self.elements_

    # Display text
    #
    def displayText(self, text:str, information:bool = True):
        # call display's method
        if self.outputs_ is not None:
            self.outputs_.displayText(text, information, self.elements_)

    # Show resolution stats
    #
    def showStats(self, params : opts, sStats : stats ):
        if self.outputs_ is not None:
            self.outputs_.showStats(params, sStats)

    # What can we do ?
    #
    def allowEdition(self) -> bool :
        return False if self.outputs_ is None else self.outputs_.allowEdition()

    def allowFolderBrowsing(self)->bool :
        return False if self.outputs_ is None else self.outputs_.allowFolderBrowsing()

    #
    # Events
    #

    # Waiting for a keyboard event (or exit event)
    #
    def waitForKeyDown(self):
        if not self.outputs_ is None:
            self.outputs_.waitForEvent(self.elements_, allEvents=True)

    # Get the list of pending events
    #
    def getEvents(self):
        # No output manager => no event;
        return [] if self.outputs_ is None else self.outputs_.getEvents()

    #
    # Outputs
    #


    # End of outputs
    #
    def close(self):
        if not self.outputs_ is None:
            self.outputs_.close()

    # Display the grid and its content
    #
    def displayGrid(self):
        if self.outputs_ is not None:
            self.outputs_.draw(self.elements_)

    # Update drawings
    def flip(self):
        if self.outputs_ is not None:
            self.outputs_.flip()




    # Try to solve the grid
    #
    #   return a tuple (found a solution ?, game escaped ?, #attempts, duration in s.)
    #
    def resolve(self)->tuple[bool, bool, int, float]:
        if self.outputs_ is None:
            return False, False, 0, 0.0

        escaped = False
        found = True  # We assume we'll find a solution !

        # for stats
        self.attempts_ = 0
        self.start_ = time.time()
        endTime = 0

        self.outputs_.startedSolving(self.elements_)

        # Let's go
        try:
            if opts.PROGRESS_MULTITHREADED == self.progressMode():
                # multithreading is just for drawings !!!
                self._resolveMultiThreaded()
            else:
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

    #
    # Internal methods
    #

    #
    # Solve the grid (internal method without exceptions handling)
    #

    # Single Threaded mode (default)
    def _resolveSingleThreaded(self):

        if self.outputs_ is None:
            return

        candidate = 0
        position = pointer(gameMode=True)
        position = self._findFirstEmptyPos(position)

        # All the elements "before" the current position are set with possible/allowed values
        # we'll try to put the "candidate" value at the current position
        while True:
            # Stopped ?
            status = self.outputs_.keyPressed()
            if True == status[0] and status[1] is not None and self.outputs_.EDIT_CANCEL == status[1].key:
                sys.exit(0)

            candidate += 1
            if candidate > VALUE_MAX:
                # No possible value found at this position
                # we'll have to go backward, to the last value setted
                position = self._previousPos(position)

                # candidate value = prev. value (incremented at next occurence)
                candidate = self.elements_[position.index()].empty()
            else:
                # Try to put the "candidate" value at current position
                #
                if True == self._checkValue(position, candidate):
                    # possible !!!
                    self.attempts_ += 1

                    self.elements_[position.index()].setValue(candidate)

                    # Update drawings
                    if self.progressMode() != opts.PROGRESS_NONE :
                        self.outputs_.draw(self.elements_)

                    # Go to the next "empty" position
                    position = self._findFirstEmptyPos(position)

                    # At the next pos., we alawyas try the lowest possible value
                    candidate = 0

    # Multithreaded mode
    def _resolveMultiThreaded(self):

        candidate = 0
        position = pointer(gameMode=True)
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
                candidate = self.elements_[position.index()].empty()
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
    def _checkValue(self, position:pointer, value:int):
        return (
            self._checkLine(position, value)
            and self._checkRow(position, value)
            and self._checkTinySquare(position, value)
        )

    #   => in the line ?
    def _checkLine(self, position:pointer, value:int):
        idFirst = position.line() * ROW_COUNT
        for tIndex in range(ROW_COUNT):
            if self.elements_[tIndex + idFirst].num == value:
                return False
        # yes
        return True

    #  => in the row ?
    def _checkRow(self, position:pointer, value:int):
        idFirst = position.row()
        for tIndex in range(LINE_COUNT):
            if self.elements_[tIndex * ROW_COUNT + idFirst].num == value:
                return False
        # yes
        return True

    #  => in the tiny-square ?
    def _checkTinySquare(self, position:pointer, value:int):
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

        self.elements_[newPos.index()].empty()
        newPos -= 1

        # while self.elements_[newPos.index()].isOriginal():

        # Don't touch "Original" nor "Obvious" values
        while not self.elements_[newPos.index()].isChangeable():
            newPos -= 1

        # Ok
        return newPos


    #
    #   Obvious values
    #

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

    # Create outputs object (and delete existing if any)
    #
    def _createOutputsGUI(self):
        if self.outputs_ is not None:
            self.outputs_.close()
            del self.outputs_

        # Create a new one
        if self.progressMode() == opts.PROGRESS_MULTITHREADED:
            #print("Create threaded outputs handklr")
            self.outputs_ = pygameThreadedOutputs()
        else:
            #print("Create unthreaded outputs handklr")
            self.outputs_ = pygameOutputs()

        self.outputs_.startUI()   # Let's go



# EOF
