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
    GRID_SIZE,
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

TESSERACT_CONFIG = "--psm 6 -c tessedit_char_whitelist=123456789"  # OCR parameters
TESSERACT_BOX_THICKNESS = 1
TESSERACT_BOX_COLOR = (0, 255, 0)


#   sudoku : Edition and/or resolution of a single sudoku grid
#
class sudoku:
    # Edition status
    #
    EDIT_CONTINUE:int = statusbits.STATUS_NONE
    EDIT_MODIFIED:int = 1  # Grid has been modified (at least once)
    EDIT_STOP:int = 2  # Stop edition
    EDIT_ESCAPE:int = 4  # Escape edition
    EDIT_ESCAPED:int = EDIT_STOP | EDIT_ESCAPE
    EDIT_NOREDRAW:int = 8  # don't redraw at previous pos value

    # Consts
    #
    VALUE_SEPARATOR:str = ","  # Value separator in files
    FILE_COMMENTS:str = "#"  # Comment lines start with

    # Construction
    #
    def __init__(self, progressMode:int = options.PROGRESS_NONE, initOutputs:bool = True):

        self.gridFileName_ : str | None = None
        self.outputs_ = None

        self.attempts_:int = 0
        self.start_:float = 0.0  # Resolution start-time
        self.editStatus_:statusbits.statusBits = statusbits.statusBits(self.EDIT_CONTINUE)

        self.elements_ : list[element] = []
        self.OSInfos_ = {}  # Informations about the OS and the Window manager

        # Show progression details ?
        self.progressMode_:int = opts.PROGRESS_NONE
        self.progressMode = progressMode

        # Set display mode
        #
        if True == initOutputs:
            # Try with PYGame
            try:
                self._createPYGameOutputs()
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

        # Create the grid
        self._emptyGrid()

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

        for _ in range(GRID_SIZE):
            self.elements_.append(element())

    # Progress mode (ie. display progression ?)
    #
    @property
    def progressMode(self):
        return self.progressMode_

    @progressMode.setter
    def progressMode(self, value:int):
        # Changed ?
        if self.progressMode_ != value:
            # create a new output object ?
            newOutPut : bool = (
                value == opts.PROGRESS_MULTITHREADED
                or self.progressMode_ == opts.PROGRESS_MULTITHREADED
            )

            self.progressMode_ = value
            if newOutPut:
                self._createPYGameOutputs()

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
            self.outputs_.waitForEvent(self.elements_, allEvents=False)

    # Get the list of pending events
    #
    def getEvents(self):
        # No output manager => no event;
        return [] if self.outputs_ is None else self.outputs_.getEvents()

    #
    # Outputs
    #

    # Convert current grid to a printable string
    #
    @override
    def __str__(self)->str:
        output : str = " "
        if len(self.elements_) == GRID_SIZE:
            position = pointer(gameMode=False)
            for _ in range(LINE_COUNT):
                output += "\n"
                for _ in range(ROW_COUNT):
                    currentElement = self.elements_[position.index()]
                    output += f" {' ' if currentElement.isEmpty() else str(currentElement.num)} "
                    position += 1
            output += "\n"

        return output[1:]

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

    # Browse a folder (to find a grid)
    #
    def browse(self, folderName:str)->str:
        if not os.path.isdir(folderName) or self.outputs_ is None:
            raise sudokuError(f"{folderName} is not a valid folder")

        files : list[str] = []
        done:bool = not self.folderContent(folderName, files)
        prev:int = -1
        index:int = 0
        currentFile:str = ""
        maxIndex:int = len(files)
        clearFile:bool = False

        # Browse ...
        while not done:
            # update drawings ?
            if prev != index:
                currentFile = os.path.join(folderName, files[index])

                # load the file and update drawings
                try:
                    self.gridFromFile(currentFile)
                except sudokuError as e:
                    print(f"Sudoku Error : {e.message_}")
                except OSError as other:
                    # the file is not valid => remove it from the list
                    print(f"Invalid file : {other}")
                    _ = files.pop(index)
                    maxIndex -= 1

                prev = index

            if 0 == maxIndex:
                # Nothing left in the folder
                # return currentFile
                done = True

            index, done, clearFile = self._browseFolder_handleKeyBoard(index, maxIndex)

        return "" if clearFile else currentFile

    # Wait for keyboard event while browsing a folder
    #
    def _browseFolder_handleKeyBoard(self, index:int, maxIndex:int):
        clearFile : bool = False
        done : bool = False

        if self.outputs_ is not None:
            event = self.outputs_.waitForEvent(self.elements_, allEvents=True)

            if event.type == self.outputs_.EVT_KEYDOWN:
                if self.outputs_.MOVE_RIGHT == event.key:
                    index += 1
                    if index >= maxIndex:
                        index = 0
                else:
                    if self.outputs_.MOVE_LEFT == event.key:
                        index -= 1
                        if index < 0:
                            index = maxIndex - 1
                    else:
                        # Cancel
                        if self.outputs_.EDIT_CANCEL == event.key:
                            done = True
                            clearFile = True
                        else:
                            # Choose the grid (for edition or solving)
                            if self.outputs_.EDIT_QUIT_AND_SAVE == event.key:
                                done = True

            elif event.type == self.outputs_.EVT_QUIT:
                done = True
                clearFile = True

        return (index, done, clearFile)

    # Read a grid'file
    #
    def load(self, fileName : str | None, mustExist : bool, showFileName:bool = True):
        if fileName is None or 0 == len(fileName):
            # ???
            raise sudokuError("No valid file name")

        if os.path.isdir(fileName):
            raise sudokuError(f"{fileName} is not a valid file")

        self.gridFileName_ = fileName

        # Open and read the file
        #
        try:
            with open(fileName) as file:
                pt = pointer(gameMode=False)

                # Read the lines
                for line in file:
                    # Not a comment !
                    if line[0] != self.FILE_COMMENTS:
                        # remove EOL
                        if line[len(line) - 1] == "\n":
                            line = line[: len(line) - 1]

                        values = line.split(self.VALUE_SEPARATOR)

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
                return

        # file.close()

        if self.outputs_ is not None and showFileName:
            self.outputs_.setGridName(self.gridFileName_)

    # Save the file
    #
    #   return the name of the saved file or None if an error occured
    #
    def save(self, genName:bool = False, comments:list[str] | None = None, newFileName:str | None = None):

        if self.gridFileName_ is None:
            return None

        # A new name ?
        if newFileName is not None:
            self.gridFileName_ = newFileName
            # self.outputs_.setGridName(newFileName, create=True)

        fileName = self.gridFileName_
        if genName:
            fileName += FILE_EXPORT_EXTENSION
        try:
            with open(fileName, "w") as file:
                # a few comments ?
                if comments and len(comments):
                    for comment in comments:
                        line = self.FILE_COMMENTS
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
                        line += self.VALUE_SEPARATOR
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

    # Edit / modify the grid
    #
    #   Returns the tuple of booleans : (escaped ?, grid saved (or successfully edited) ?)
    #
    def edit(self) -> tuple[bool, bool]:
        # Can we edit this grid
        if self.outputs_ is None or False == self.outputs_.allowEdition():
            return (False, False)

        # Edition
        #
        currentPos : pointer = pointer(gameMode=False)  # current position
        prevPos : pointer | None =  None  # previous pos (if erase needed)
        self.editStatus_.value = self.EDIT_CONTINUE

        while not self.editStatus_.isSet(self.EDIT_STOP):
            # if sel. changed, erase previously selected element
            self._edit_updatePos(
                None if self.editStatus_.isSet(self.EDIT_NOREDRAW) else prevPos,
                currentPos,
            )
            prevPos = copy.deepcopy(currentPos)   # // copy constructor
            self.editStatus_.remove(self.EDIT_NOREDRAW)

            # Wait for an event
            event = self.outputs_.pollEvent()

            # By a mouse click ?
            if self.outputs_.EVT_MOUSEBUTTONDOWN == event.type:
                button, pos = self.outputs_.mouseButtonStatus(event)
                if button == self.outputs_.MOUSE_BUTTON_LEFT:
                    currentPos.moveTo(pos=self.outputs_.mousePosition(pos))
            else:
                # With the keyboard
                if self.outputs_.EVT_KEYDOWN == event.type:
                    match event.key:
                        case self.outputs_.MOVE_LEFT:
                            currentPos.decRow()
                        case self.outputs_.MOVE_RIGHT:
                            currentPos.incRow()
                        case self.outputs_.MOVE_UP:
                            currentPos.decLine()
                        case self.outputs_.MOVE_DOWN:
                            currentPos.incLine()
                        case key if key in range(
                            self.outputs_.VALUE_1, self.outputs_.VALUE_9 + 1
                        ):
                            self._edit_setValue(
                                currentPos, key - self.outputs_.VALUE_1 + 1
                            )
                        case self.outputs_.VALUE_DEC:
                            self._edit_decValue(currentPos)
                        case self.outputs_.VALUE_INC:
                            self._edit_incValue(currentPos)
                        case self.outputs_.REMOVE_VALUE:
                            self._edit_removeValue(currentPos)
                        case self.outputs_.EDIT_CANCEL:
                            self.editStatus_.set(self.EDIT_ESCAPED)
                        case self.outputs_.EDIT_QUIT_AND_SAVE:
                            self.editStatus_.set(self.EDIT_STOP)
                        case _:
                            pass

                elif event.type == self.outputs_.EVT_QUIT:
                    self.editStatus_.set(self.EDIT_ESCAPED)

        escaped = self.editStatus_.isSet(self.EDIT_ESCAPE)
        if not escaped:
            value : int | None = self.elements_[currentPos.index()].num
            if value is not None:
                self.outputs_.drawSingleElement(
                    currentPos.row(),
                    currentPos.line(),
                    value,
                    self.outputs_.BK_COLOUR,
                    self.outputs_.HILITE_COLOUR,
                )
                self.outputs_.update()

        # Saves changes or exit
        return (
            escaped,
            ((self.save() is not None) if self.editStatus_.isSet(self.EDIT_MODIFIED) else True)
            if not escaped
            else False,
        )

    # Load a grid stored in a file
    #
    #   return True if grid has been successfully loaded
    #
    def gridFromFile(self, fileName : str, nameOnGrid:bool=True) -> bool:
        self.emptyGrid()

        try:
            self.load(fileName, True, False)
        except UnicodeDecodeError:
            return False
        except sudokuError as se:
            print(f"Sudoku Error : {se.message_}")
            return False

        if self.outputs_ is not None:
            if nameOnGrid:
                self.outputs_.setGridName(fileName)
            self.outputs_.drawBackground()
            self.outputs_.draw(self.elements_)
            self.outputs_.update()
        return True

    # Empties the grid
    #
    def emptyGrid(self):
        for el in self.elements_:
            el.empty()

    # Return to the original state
    #
    def revertGrid(self):
        for el in self.elements_:
            if not el.isOriginal():
                el.empty()

    # Find all the obvious values
    #
    #   return a tuple (#obvious values, duration in s.)
    #
    def findObviousValues(self):

        # for stats
        found = 0
        self.start_ = time.time()

        values = 1
        while 0 < values:
            values = self._findObviousValues()
            found += values

        # Find a solution !!!
        return found, time.time() - self.start_

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
            if opts.PROGRESS_MULTITHREADED == self.progressMode:
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

    # Get the list of possible values at a given position
    #
    def getValues(self, position:pointer)->list[int]:
        values : list[int] = []

        for value in range(VALUE_MIN, VALUE_MAX):
            if self._checkValue(position, value):
                # This value can be used
                values.append(value)

        # return the list
        return values

    # List of grids in a folder
    #   fill the {files} with {folder} content
    #
    #   return True if the list is not empty, False in all other cases
    def folderContent(self, folder:str, files:list[str])->bool:
        files.clear()

        # Folder content
        if len(folder) > 0:
            # Only this folder
            for _, _, fileNames in os.walk(folder):
                files.extend(fileNames)
                break

        # No solution files in the list !
        for file in files:
            _, fileExt = os.path.splitext(file)
            if FILE_EXPORT_EXTENSION == fileExt:
                # remove the file from the list
                files.remove(file)

        files.sort()
        return len(files) > 0

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
                    if self.progressMode != opts.PROGRESS_NONE :
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

    # Create PYGameOutputs object (and delete existing if any)
    #
    def _createPYGameOutputs(self):
        if self.outputs_ is not None:
            self.outputs_.close()
            del self.outputs_

        # Instantiate new one
        self.outputs_ = (
            pygameThreadedOutputs()
            if self.progressMode == opts.PROGRESS_MULTITHREADED
            else pygameOutputs()
        )

    # Update grid during edition
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        if self.outputs_ is not None and prevPos is not None:
            # if sel. changed, erase previously selected element
            self.outputs_.drawSingleElement(
                prevPos.row(),
                prevPos.line(),
                self.elements_[prevPos.index()].num,
                self.outputs_.BK_COLOUR,
                self.outputs_.HILITE_COLOUR,
            )

            # Hilight the new value
            self.outputs_.drawSingleElement(
                currentPos.row(),
                currentPos.line(),
                self.elements_[currentPos.index()].num,
                self.outputs_.SEL_BK_COLOUR,
                self.outputs_.HILITE_COLOUR,
            )
            self.outputs_.update()

    # (try to) set a value
    def _edit_setValue(self, pos: pointer, val: int):
        """
        if self.outputs_ is not None:
            if val == 0:
                self._edit_removeValue(pos)
                #print(f"Val : {val}")
            elif"""
        if self._checkValue(pos, val):
            self.elements_[pos.index()].setValue(val, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Decrease value
    def _edit_decValue(self, pos: pointer):
        val = self.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal = self._findPreviousValue(pos, val)
        if newVal != val:
            self.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Inc value
    def _edit_incValue(self, pos: pointer):
        val = self.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal = self._findNextValue(pos, val)
        if newVal != val:
            self.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    def _edit_removeValue(self, pos: pointer):
        self.elements_[pos.index()].setValue(0, element.STATUS_ORIGINAL, True)
        self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)


# EOF
