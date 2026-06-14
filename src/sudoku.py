#!/usr/bin/python3
#
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

import os, time, math

from element import element
from pointer import pointer, LINE_COUNT, ROW_COUNT, GRID_SIZE, VALUE_MIN, VALUE_MAX, INDEX_MAX
from tinySquare import tinySquare
from ownExceptions import reachedEndOfList, sudokuError
from options import FILE_EXPORT_EXTENSION, options as opts
from pygameOutputs import pygameOutputs
from pygameThreadedOutputs import pygameThreadedOutputs
from sharedTools import statusBits

#
# OCR
#
import cv2
import pytesseract
from pytesseract import Output

TESSERACT_CONFIG = "--psm 6 -c tessedit_char_whitelist=123456789"       # OCR parameters
TESSERACT_BOX_THICKNESS = 1
TESSERACT_BOX_COLOR = (0,255,0)

#   sudoku : Edition and/or resolution of a single sudoku grid
#
class sudoku(object):

    # Edition status
    #
    EDIT_CONTINUE   = statusBits.STATUS_NONE
    EDIT_MODIFIED   = 1         # Grid has been modified (at least once)
    EDIT_STOP       = 2         # Stop edition
    EDIT_ESCAPE     = 4         # Escape edition
    EDIT_ESCAPED    = (EDIT_STOP|EDIT_ESCAPE)
    EDIT_NOREDRAW   = 8         # don't redraw at previous pos value

    # Consts
    #
    VALUE_SEPARATOR = ","       # Value separator in files
    FILE_COMMENTS = "#"         # Comment lines start with

    # Members
    #
    gridFileName_ = None
    elements_ = []          # The grid (as a flat list)
    outputs_ = None

    attempts_ = 0
    start_ = 0              # Resolution start-time

    progressMode_ = opts.PROGRESS_NONE  # Draw grid during solving process ?

    OSInfos_ = {}           # Informations about the OS and the Window manager

    editStatus_ = statusBits.statusBits(EDIT_CONTINUE)

    # Construction
    #
    def __init__(self, progressMode = opts.PROGRESS_NONE, initOutputs = True):

        # Show progression details ?
        self.progressMode = progressMode

        # Set display mode
        #
        if True == initOutputs:
            # Try with PYGame
            try:
                self._createPYGameOutputs()
            except ModuleNotFoundError:
                print("PYGame isn't installed. Try pip install pygame")
                exit()
            except sudokuError as e:
                print(e)

            if self.outputs_ is None:
                exit()

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
    def progressMode(self, value):
        # Changed ?
        if self.outputs_ is not None and self.progressMode_ != value:
            # create a new output object ?
            newOutPut = value == opts.PROGRESS_MULTITHREADED or self.progressMode_ == opts.PROGRESS_MULTITHREADED

            self.progressMode_ = value
            if newOutPut:
                self._createPYGameOutputs()

    # Filename (of the source grid)
    #
    def fileName(self):
        return self.gridFileName_

    # Access
    #
    def outputs(self):
        return self.outputs_
    def grid(self):
        return self.elements_

    # Display text
    #
    def displayText(self, text, information = True):
        # call display's method
        if self.outputs_ is not None:
            self.outputs_.displayText(text, information, self.elements_)

    # Show resolution stats
    #
    def showStats(self, params, sStats):
        if self.outputs_ is not None:
            self.outputs_.showStats(params, sStats)

    # What can we do ?
    #
    def allowEdition(self):
        return False if self.outputs_ is None else self.outputs_.allowEdition()
    def allowFolderBrowsing(self):
        return False if self.outputs_ is None else self.outputs_.allowFolderBrowsing()

    #
    # Events
    #

    # Waiting for a keyboard event (or exit event)
    #
    def waitForKeyDown(self):
        if not self.outputs_ is None:
            self.outputs_.waitForEvent(self.elements_, allEvents = False)

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
    def __str__(self):
        output = "";
        if len(self.elements_) == GRID_SIZE:
            position = pointer(gameMode = False)
            for line in range(LINE_COUNT):
                output+="\n"
                for row in range(ROW_COUNT):
                    currentElement = self.elements_[position.index()]
                    output+=f" {' ' if currentElement.isEmpty() else str(currentElement.value())} "
                    position+=1
            output+="\n"

        return output

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
    def browse(self, folderName): # noqa
        if not os.path.isdir(folderName) or self.outputs_ is None:
            raise sudokuError(f"{folderName} is not a valid folder")

        files = []
        done = (False == self.folderContent(folderName, files))

        prev = -1
        index = 0
        currentFile = ""
        maxIndex = len(files)
        clearFile = False

        # Browse ...
        while not done:
            # update drawings ?
            if  prev != index:
                currentFile = os.path.join(folderName, files[index])

                # load the file and update drawings
                try:
                    self.gridFromFile(currentFile)
                except sudokuError as e:
                    print(f"Sudoku Error : {e.message}")
                except:
                    # the file is not valid => remove it from the list
                    files.pop(index)
                    maxIndex-=1

                prev = index

            if 0 == maxIndex or self.outputs_ is None:
                # Nothing left in the folder
                #return currentFile
                done = True

            index, done, clearFile = self._browseFolder_handleKeyBoard(index, maxIndex)

        return "" if clearFile else currentFile

    # Wait for keyboard event while browsing a folder
    #
    def _browseFolder_handleKeyBoard(self, index, maxIndex):

        clearFile = False
        done = False

        if self.outputs_ is not None:
            event = self.outputs_.waitForEvent(self.elements_, allEvents = True)

            if event.type == self.outputs_.EVT_KEYDOWN:
                if self.outputs_.MOVE_RIGHT == event.key:
                    index+=1
                    if index >= maxIndex:
                        index = 0
                else:
                    if self.outputs_.MOVE_LEFT == event.key:
                        index-=1
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
    def load(self, fileName, mustExist, showFileName = True):
        if fileName is None or 0 == len(fileName):
            # ???
            raise sudokuError("No valid file name")

        if os.path.isdir(fileName):
            raise sudokuError(f"{fileName} is not a valid file")

        self.gridFileName_ = fileName

        # Open and read the file
        #
        try:
            file = open(fileName)
        except FileNotFoundError:
            if True == mustExist:
                raise sudokuError(f"The file '{fileName}' doesn't exist")
            else:
                print(f"New file : '{fileName}'")
                return

        pt = pointer(gameMode = False)

        # Read the lines
        for line in file:

            # Not a comment !
            if line[0] != self.FILE_COMMENTS :
                # remove EOL
                if line[len(line) - 1] == "\n":
                    line = line[:len(line) - 1]

                values = line.split(self.VALUE_SEPARATOR)

                if not ROW_COUNT == len(values):
                    raise sudokuError(f"Invalid format for line n° {str(pt.line()+1)} - {str(len(values))} values")

                for val in values:
                    self._setAt(pt, val)

                    # Next value
                    pt += 1

        file.close()

        if self.outputs_ is not None and showFileName:
            self.outputs_.setGridName(self.gridFileName_)

    # Save the file
    #
    #   return the name of the saved file or None if an error occured
    #
    def save(self, genName = False, comments = None, newFileName = None):

        if self.gridFileName_ is None:
            return None

        # A new name ?
        if newFileName is not None:
            self.gridFileName_ = newFileName
            #self.outputs_.setGridName(newFileName, create=True)

        fileName = self.gridFileName_
        if genName :
            fileName += FILE_EXPORT_EXTENSION
        try:
            file = open(fileName, "w")

            # a few comments ?
            if comments and len(comments):
                for comment in comments:
                    line = self.FILE_COMMENTS
                    line+=" "
                    line+=comment
                    line+="\n"
                    file.write(line)

            # File content
            pt = pointer(gameMode = False)
            for lIndex in range(LINE_COUNT) :
                line = ""
                for _ in range(ROW_COUNT):
                    el = self.elements_[pt.index()]
                    line+=str(0 if el.isEmpty() else el.value())
                    line+=self.VALUE_SEPARATOR
                    pt+=1

                # add separator
                line = line[:len(line) - 1]
                if lIndex < (LINE_COUNT -1):
                    line+="\n"

                file.write(line)

            file.close()
            return fileName
        except ModuleNotFoundError:
            raise sudokuError(f"io error while writing the file '{fileName}'")

    # Edit / modify the grid
    #
    #   Returns the tuple of booleans : (escaped ?, grid saved (or successfully edited) ?)
    #
    def edit(self):
        # Can we edit this grid
        if self.outputs_ is None or False == self.outputs_.allowEdition():
            return False, False

        # Edition
        #
        currentPos = pointer(gameMode=False)      # current position
        prevPos = None                            # previous pos (if erase needed)

        self.editStatus_.value = self.EDIT_CONTINUE

        while not self.editStatus_.isSet(self.EDIT_STOP):
            # if sel. changed, erase previously selected element
            self._edit_updatePos(None if self.editStatus_.isSet(self.EDIT_NOREDRAW) else prevPos, currentPos)
            prevPos = pointer(currentPos)
            self.editStatus_.remove(self.EDIT_NOREDRAW)

            # Wait for an event
            event = self.outputs_.pollEvent()

            # By a mouse click ?
            if self.outputs_.EVT_MOUSEBUTTONDOWN == event.type:
                button, pos = self.outputs_.mouseButtonStatus(event)
                if button == self.outputs_.MOUSE_BUTTON_LEFT:
                    currentPos.moveTo(pos = self.outputs_.mousePosition(pos))
            else:
                # With the keyboard
                if self.outputs_.EVT_KEYDOWN == event.type:
                    match event.key:
                        case self.outputs_.MOVE_LEFT :
                            currentPos.decRow()
                        case self.outputs_.MOVE_RIGHT :
                            currentPos.incRow()
                        case self.outputs_.MOVE_UP :
                            currentPos.decLine()
                        case self.outputs_.MOVE_DOWN :
                            currentPos.incLine()
                        case key if key in range(self.outputs_.VALUE_1 , self.outputs_.VALUE_9+1) :
                            self._edit_setValue(currentPos, key - self.outputs_.VALUE_1 + 1)
                        case self.outputs_.VALUE_DEC :
                            self._edit_decValue(currentPos)
                        case self.outputs_.VALUE_INC :
                            self._edit_incValue(currentPos)
                        case self.outputs_.REMOVE_VALUE :
                            self._edit_removeValue(currentPos)
                        case self.outputs_.EDIT_CANCEL :
                           self.editStatus_.set(self.EDIT_ESCAPED)
                        case self.outputs_.EDIT_QUIT_AND_SAVE :
                            self.editStatus_.set(self.EDIT_STOP)
                        case _ :
                            pass

                elif event.type == self.outputs_.EVT_QUIT:
                    self.editStatus_.set(self.EDIT_ESCAPED)

        escaped = self.editStatus_.isSet(self.EDIT_ESCAPE)
        if not escaped :
            self.outputs_.drawSingleElement(currentPos.row(), currentPos.line(), self.elements_[currentPos.index()].value(), self.outputs_.BK_COLOUR, self.outputs_.HILITE_COLOUR)
            self.outputs_.update()

        # Saves changes or exit
        return (escaped, (self.save() if self.editStatus_.isSet(self.EDIT_MODIFIED) else True) if not escaped else False)

    # Load a grid stored in a file
    #
    #   return True if grid has been successfully loaded
    #
    def gridFromFile(self, fileName, nameOnGrid = True) -> bool:
        self.emptyGrid()

        try:
            self.load(fileName, True, False)
        except UnicodeDecodeError:
            return False
        except sudokuError as se:
            print(f"Sudoku Error : {se.message}")
            return False

        if self.outputs_ is not None:
            if nameOnGrid:
                self.outputs_.setGridName(fileName)
            self.outputs_._drawBackground()
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
    def resolve(self):

        if self.outputs_ is None or self.elements_ is None:
            return False, False, 0, 0.0

        escaped = False
        found = True        # We assume we'll find a solution !

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
        except:
            escaped = True

        # Finished (anyway)
        return (found, escaped, self.attempts_, endTime)

    # Get the list of possible values at a given position
    #
    def getValues(self, position):
        values = []

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
    def folderContent(self, folder, files):
        files.clear()

        # Folder content
        if len(folder) > 0:
            # Only this folder
            for (_, _, fileNames) in os.walk(folder):
                files.extend(fileNames)
                break

        # No solution files in the list !
        for file in files :
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
        position = pointer(gameMode = True)
        position = self._findFirstEmptyPos(position)

        # All the elements "before" the current position are set with possible/allowed values
        # we'll try to put the "candidate" value at the current position
        while True :

            # Stopped ?
            status = self.outputs_.keyPressed()
            if True == status[0] and self.outputs_.EDIT_CANCEL == status[1].key:
                exit(0)

            candidate+=1
            if candidate > VALUE_MAX:

                # No possible value found at this position
                # we'll have to go backward, to the last value setted
                position = self._previousPos(position)

                # candidate value = prev. value (incremented at next occurence)
                candidate = self.elements_[position.index()].empty()
            else :
                # Try to put the "candidate" value at current position
                #
                if True == self._checkValue(position, candidate):
                    # possible !!!
                    self.attempts_ += 1

                    self.elements_[position.index()].setValue(candidate)

                    # Update drawings
                    if self.progressMode != opts.PROGRESS_NONE and self.outputs_ is not None:
                        self.outputs_.draw(self.elements_)

                    # Go to the next "empty" position
                    position = self._findFirstEmptyPos(position)

                    # At the next pos., we alawyas try the lowest possible value
                    candidate = 0


    # Multithreaded mode
    def _resolveMultiThreaded(self):

        candidate = 0
        position = pointer(gameMode = True)
        position = self._findFirstEmptyPos(position)

        # All the elements "before" the current position are set with possible/allowed values
        # we'll try to put the "candidate" value at the current position
        while True :
            candidate+=1

            if candidate > VALUE_MAX:

                # No possible value found at this position
                # we'll have to go backward, to the last value setted
                position = self._previousPos(position)

                # candidate value = prev. value (incremented at next occurence)
                candidate = self.elements_[position.index()].empty()
            else :
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
    def _checkValue(self, position, value):
        return self._checkLine(position, value) and self._checkRow(position, value) and self._checkTinySquare(position, value)

    #   => in the line ?
    def _checkLine(self, position, value):
        idFirst = position.line() * ROW_COUNT
        for tIndex in range(ROW_COUNT):
            if self.elements_[tIndex + idFirst].value() == value:
                return False
        # yes
        return True

    #  => in the row ?
    def _checkRow(self, position, value):
        idFirst = position.row()
        for tIndex in range(LINE_COUNT):
            if self.elements_[tIndex * ROW_COUNT + idFirst].value() == value:
                return False
        # yes
        return True

    #  => in the tiny-square ?
    def _checkTinySquare(self, position, value):
        # Search in my tiny-square
        mySquare = tinySquare(position.squareID())
        return False == mySquare.inMe(self.elements_, value)

    # (try to) set a value at current position
    def _setAt(self, position, val, warn = True) -> bool:
        # Check the value
        if isinstance(val, int) :
            value = val
        else:
            if not val.isnumeric():
                if warn:
                    raise sudokuError(f"Error : the value in ({str(position.line() + 1)},{str(position.row()+1)}) is not numeric")
                return False

            value = int(val)

        # in [0,9] ?
        value = int(val)
        if (value < 0 or value > 9):
            if warn:
                raise sudokuError(f"Value Error : {value} is not in the valid range in ({str(position.line() + 1)},{str(position.row()+1)})")
            return False

        if value > 0:
            # Check the line
            if False == self._checkLine(position, value):
                if warn:
                    raise sudokuError(f"Line value error : value {value} can't be set in ({str(position.line() + 1)},{str(position.row()+1)})")
                return False;

            # Check the row
            if False == self._checkRow(position, value):
                if warn:
                    raise sudokuError(f"Row value error : value {value} can't be set in ({str(position.line() + 1)},{str(position.row()+1)})")
                return False

            # Check the tiny-square
            if False == self._checkTinySquare(position, value):
                if warn:
                    raise sudokuError(f"Square value error : value {value} can't be set in ({str(position.line() + 1)},{str(position.row()+1)})")
                return False

            # Set the value
            self.elements_[position.line() * ROW_COUNT + position.row()].setValue(value, element.STATUS_ORIGINAL)
            return True

        return False    # Value not set

    # Find the next empty pos.
    #
    #   Returns a pointer to the found position
    #   An exception reachedEndOfList is raised when the grid is full (the game is over and a solution has been found)
    #
    def _findFirstEmptyPos(self, start):
        newPos = pointer(start)
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
    def _previousPos(self, current):
        newPos = pointer(current)

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
    def _findNextValue(self, position, val):
        nextVal = position.incValue(val)
        while not val == nextVal:
            if self._checkValue(position, nextVal):
                return nextVal
            # try the next value
            nextVal = position.incValue(nextVal)

        return nextVal

    # Find the lowest possible value for an element
    #
    def _findPreviousValue(self, position, val):
        nextVal = position.decValue(val)
        while not val == nextVal:
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
    def _findObviousValues(self):
        found = 0

        position = pointer()

        for index in range(INDEX_MAX):
            if self.elements_[position.index()].isEmpty():
                # Try to set a single value at this empty place
                value = self._checkObviousValue(position)

                if not value is None:
                    # One more obvious value !!!!
                    self.elements_[position.index()].setValue(value, element.STATUS_OBVIOUS)
                    found += 1
            else:

                value = self.elements_[position.index()].value()

                # Can we put this value on another line ?
                found += self._setObviousValueInLines(position, value)

                # ... or/and put it in another col ?
                found += self._setObviousValueInRows(position, value)

            # Next pos.
            position+=1

        # End of search loop
        return found


    # Is there an obvious value for the given position ?
    #
    #      returns the value (if just one possible) or None
    #
    def _checkObviousValue(self, position):
        value = None

        for test in range(VALUE_MIN, VALUE_MAX + 1):
            if self._checkValue(position, test):
                # This value can be used
                if value :
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
    def _setObviousValueInLines(self, position, value):
        # "little" squares IDs for this line
        modID = position.squareID() % 3
        if 0 ==  modID:
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
        firstPos = firstSquare.findValue(self.elements_, value)
        secondPos = secondSquare.findValue(self.elements_, value)

        # None of them or both of them
        if (firstPos[0] is None and secondPos[0] is None) or (not firstPos[0] is None and  not secondPos[0] is None) :
            return 0

        # Just one square misses the value => we'll try to put this value in the correct line
        #
        #   The sum of the 3 lineID is a consts and we know 2 oh them
        #
        if firstPos[0] is None:
            candidate = firstSquare
            candidateLine = 2 * (firstSquare.topLine() + 1) - secondPos[0] - position.line() + 1
        else:
            candidate = secondSquare
            candidateLine = 2 * (secondSquare.topLine() + 1) - firstPos[0] - position.line() + 1

        # Try to put the value ...
        #
        foundPos = None
        pos = pointer(index = 0)
        pos.moveTo(candidateLine, candidate.topRow())

        try:
            for _ in range(tinySquare.TINY_ROW_COUNT):
                if  self.elements_[pos.index()].isEmpty() and self._checkValue(pos, value):
                    if None != foundPos:
                        # Already a candiate => not obvious
                        return 0
                    foundPos = pointer(other = pos) # call the copy constructor !!!

                # Next row
                pos+=1
        except reachedEndOfList:      # Might go out of range and raise reachedEndOfList exception
            pass

        # Did we find a position ?
        if foundPos is not None:
            # Yes !!!
            self.elements_[foundPos.index()].setValue(value, element.STATUS_OBVIOUS)
            return 1

        # No ...
        return 0

    # Try to put the value in another row
    #
    #   return the count (0 or 1) of value set
    #
    def _setObviousValueInRows(self, position, value):
        # "little" squares IDs for this line
        modID = math.floor(position.squareID() / 3)
        if 0 ==  modID:
            # At the top pos
            firstSquare = tinySquare(position.squareID() + tinySquare.TINY_ROW_COUNT)
            secondSquare = tinySquare(position.squareID() + 2 * tinySquare.TINY_ROW_COUNT)
        else:
            if 1 == modID:
                # centered
                firstSquare = tinySquare(position.squareID() - tinySquare.TINY_ROW_COUNT)
                secondSquare = tinySquare(position.squareID() + tinySquare.TINY_ROW_COUNT)
            else:
                # on the bottom
                firstSquare = tinySquare(position.squareID() - 2 * tinySquare.TINY_ROW_COUNT)
                secondSquare = tinySquare(position.squareID() - 1 * tinySquare.TINY_ROW_COUNT)

        # Is the value already in theses squares ?
        firstPos = firstSquare.findValue(self.elements_, value)
        secondPos = secondSquare.findValue(self.elements_, value)

        # None of them or both of them
        if (firstPos[0] is None and secondPos[0] is None) or (not firstPos[0] is None and not secondPos[0] is None) :
            return 0

        # Just one square misses the value => we'll try to put this value in the correct line
        #
        #   The sum of the 3 lineID is a consts and we know 2 of them
        #
        if firstPos[0] is None:
            candidate = firstSquare
            candidateRow = 2 * (firstSquare.topRow() + 1) - secondPos[1] - position.row() + 1
        else:
            candidate = secondSquare
            candidateRow = 2 * (secondSquare.topRow() + 1) - firstPos[1] - position.row() + 1

        # Try to put the value ...
        #
        foundPos = None
        pos = pointer(index = 0)
        pos.moveTo(candidate.topLine(), candidateRow)

        try:
            for _ in range(tinySquare.TINY_LINE_COUNT):
                if  self.elements_[pos.index()].isEmpty() and self._checkValue(pos, value):
                    if None != foundPos:
                        # Already a candiate => not obvious
                        return 0

                    foundPos = pointer(other = pos) # call the copy constructor !!!

                # Next line
                pos+= ROW_COUNT  # Might go out of range and raise reachedEndOfList exception
        except reachedEndOfList:
            pass

        # Did we find a valid position ?
        if foundPos is not None:
            # Yes !!!
            self.elements_[foundPos.index()].setValue(value, element.STATUS_OBVIOUS)
            return 1

        # No ...
        return 0

    # Create PYGameOutputs object (and delete existing if any)
    #
    def _createPYGameOutputs(self):
        pos = None
        if self.outputs_ is not None:
            # Get the position of the window
            pos = self.outputs_.getWindowPosition()

            # Stop the thread (if any)
            self.outputs_.close()

            # free previous object
            del self.outputs_

        # Instantiate new one
        self.outputs_ = pygameThreadedOutputs(position = pos) if self.progressMode == opts.PROGRESS_MULTITHREADED else pygameOutputs()

    # Update grid during edition
    def _edit_updatePos(self, prevPos, currentPos):
        if self.outputs_ is not None:
            # if sel. changed, erase previously selected element
            if prevPos is not None:
                self.outputs_.drawSingleElement(prevPos.row(), prevPos.line(), self.elements_[prevPos.index()].value(), self.outputs_.BK_COLOUR, self.outputs_.HILITE_COLOUR)

            # Hilight the new value
            self.outputs_.drawSingleElement(currentPos.row(), currentPos.line(), self.elements_[currentPos.index()].value(), self.outputs_.SEL_BK_COLOUR, self.outputs_.HILITE_COLOUR)
            self.outputs_.update()

    # (try to) set a value
    def _edit_setValue(self, pos : pointer, val : int):
        """
        if self.outputs_ is not None:
            if val == 0:
                self._edit_removeValue(pos)
                #print(f"Val : {val}")
            elif """
        if self._checkValue(pos, val):
            self.elements_[pos.index()].setValue(val, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Decrease value
    def _edit_decValue(self, pos : pointer):
        val = self.elements_[pos.index()].value()
        if val is None :
            val = 0

        newVal = self._findPreviousValue(pos, val)
        if newVal != val:
            self.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Inc value
    def _edit_incValue(self, pos : pointer):
        val = self.elements_[pos.index()].value()
        if val is None :
            val = 0

        newVal = self._findNextValue(pos, val)
        if newVal != val:
            self.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    def _edit_removeValue(self, pos : pointer):
        self.elements_[pos.index()].setValue(0, element.STATUS_ORIGINAL, True)
        self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    #
    #   OCR
    #

    # Parse an image file
    #
    def gridFromImage(self, fileName, removeFrames = False, genBoxes = False) -> bool:
        if fileName is None:
            return False

        img = cv2.imread(fileName)
        if img is not None:
            if removeFrames:
                img = self._removeFrames(img)
                if img is None:
                    return False

            # Theorical dims of a rectangle
            dims = img.shape
            boxHeight = dims[0] / 9
            boxWidth = dims[1] / 9

            data = pytesseract.image_to_data(img, output_type=Output.DICT, config = TESSERACT_CONFIG)
            position = pointer(gameMode = False)

            for i in range(len(data["text"])):
                if data["conf"][i] != -1:
                    # Coordinates
                    x, y = data["left"][i], data["top"][i]
                    w, h = data["width"][i], data["height"][i]

                    line = (int)(y / boxHeight)
                    row = (int)(x / boxWidth)

                    text = data["text"][i]
                    tLen = len(text)

                    sWidth = (int)(w / tLen)
                    top_left = (x, y)

                    for index in range(tLen):
                        value = text[index]
                        position.moveTo(line, index + row)
                        self._setAt(position, ord(value) - ord('0'), False)     # Try to set the value in the grid

                        bottom_right = (top_left[0] + sWidth, top_left[1] + h)

                        if genBoxes:
                            cv2.rectangle(img, top_left, bottom_right, TESSERACT_BOX_COLOR, TESSERACT_BOX_THICKNESS)

                        top_left = (bottom_right[0], top_left[1])

            if genBoxes :
                # Save the image with boxes
                full = os.path.splitext(fileName)
                dst = os.path.join(full[0] + "_boxes")
                dst+= full[1]
                cv2.imwrite(dst, img)

            return True

        return False

    # Remove vertical and horizontal frames around the grid
    #
    def _removeFrames(self, img):
        result = img.copy()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Remove horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40,1))
        remove_horizontal = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        cnts = cv2.findContours(remove_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(result, [c], -1, (255,255,255), 5)

        # Remove vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1,40))
        remove_vertical = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        cnts = cv2.findContours(remove_vertical, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]
        for c in cnts:
            cv2.drawContours(result, [c], -1, (255,255,255), 5)

        return result

# EOF
