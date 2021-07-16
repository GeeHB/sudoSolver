# coding=UTF-8
#
#   File     :   sudoku.py
#
#   Author      :   JHB
#
#   Description :   sudoku object 
#                       -  edtion and/or resolution of a sudoku's grid
#
#   Version     :   0.1.28
#
#   Date        :   2020-12-24
#

import os, time

from element import element, elementStatus
from pointer import pointer
from ownExceptions import reachedEndOfList, sudokuError

from consoleOutputs import consoleOutputs

#
#   sudoku : Edition and/or resolution of a single sudoku grid
#
class sudoku(object):

    # Consts
    #
    VALUE_SEPARATOR =       ","         # Value separator in files
    FILE_EXPORT_EXTENSION = ".soluce"   # A solution grid
    FILE_COMMENTS =         "#"         # Comment lines start with


    # Members
    #
    gridFileName_ = None
    elements_ = []          # The grid (as a flat list)
    outputs_ = None

    attempts_ = 0
    start_ = 0              # Resolution start-time

    # top-left index of "small" squares
    squareIndex_ = [0, 3, 6, 27, 30, 33, 54, 57, 60]       

    # Construction
    #
    def __init__(self, detailsRatio = 0, consoleMode = False):

        # Set display mode
        #

        # Try PYGame
        if False == consoleMode:
            try:
                from pygameOutputs import pygameOutputs
                self.outputs_ = pygameOutputs()
            except ModuleNotFoundError:
                print("PYGame isn't installed, outputs will be redirected to console")
            except sudokuError as e:
                print(e)

        if None == self.outputs_:
            try:
                from cursesOutputs import cursesOutputs
                self.outputs_ = cursesOutputs()
            except ModuleNotFoundError:
                print("(n)Curses isn't installed, outputs will be redirected to the console")
            except sudokuError as e:
                print(e)
             
        # No display mode  => use console
        if None == self.outputs_:
            self.outputs_ = consoleOutputs()

        # Details
        self.outputs_.setDetailsRatio(detailsRatio)

        # Create the grid
        for _ in range(pointer.LINE_COUNT * pointer.ROW_COUNT):
            self.elements_.append(element())
        
    # Filename (of the source grid)
    #
    def fileName(self):
        return self.gridFileName_
    
    # Display text
    #
    def displayText(self, text, information = True):
        # call display's method
        self.outputs_.displayText(text, information, self.elements_)
    
    # What can we do ?
    #
    def allowEdition(self):
        return False if None == self.outputs_ else self.outputs_.allowEdition()
    def allowFolderBrowsing(self):
        return False if None == self.outputs_ else self.outputs_.allowFolderBrowsing()

    # Waiting for a keyboard event (or exit event)
    #
    def waitForKeyDown(self):
        if not None == self.outputs_:
            self.outputs_.waitForEvent(self.elements_, allEvents = False)

    # End of outputs
    #
    def close(self):
        if not None == self.outputs_:
            self.outputs_.close()
    
    # Display the grid and its content
    #
    def showGrid(self):
        self.outputs_.draw(self.elements_)

    # Browse a folder (to find a grid)
    #
    def browse(self, folderName):
        if not os.path.isdir(folderName):
            raise sudokuError(folderName + " is not a valid folder")

        files = []
        
        # Only this folder
        for (_, _, fileNames) in os.walk(folderName):
            files.extend(fileNames)
            break

        # No soluce files in the list !
        for file in files:
            _, fileExt = os.path.splitext(file)
            if self.FILE_EXPORT_EXTENSION == fileExt:
                # remove the file from the list
                files.remove(file)

        prev = -1
        index = 0
        done = len(files) <= index   # is the folder empty ?
        currentFile = ""
        while not done:
            # update drawings ?
            if  prev != index:
                currentFile = os.path.join(folderName, files[index])

                # load the file
                try:
                    self._emptyGrid()
                    self.load(currentFile, True)
                    self.outputs_.setGridName(currentFile)
                    self.outputs_._drawBackground()
                    self.outputs_.draw(self.elements_)
                    self.outputs_.update()
                    prev = index
                except:
                    # the file is not valid => remove it from the list
                    files.pop(index)
            
            if 0 == len(files):
                # Nothing left in the folder
                done = True
            else:
                
                # Wait for keyboard event
                #
                event = self.outputs_.waitForEvent(self.elements_, allEvents = True)
                
                if event.type == self.outputs_.EVT_KEYDOWN:
                    if self.outputs_.MOVE_RIGHT == event.key:
                        index+=1
                    else:                    
                        if self.outputs_.MOVE_LEFT == event.key:
                            index-=1
                        else:
                            # Cancel
                            if self.outputs_.EDIT_CANCEL == event.key:
                                done = True
                                currentFile = "" 
                            else:
                                # Choose the grid (for edition or solving)
                                if self.outputs_.EDIT_QUIT_AND_SAVE == event.key:
                                    done = True                                                            
                elif event.type == self.outputs_.EVT_QUIT: 
                    done = True
                    currentFile = "" 
                
                # stay in the folder
                if index < 0:
                    index = len(files) - 1
                elif index >= len(files):
                    index = 0

        return currentFile
    
    # Read a grid'file
    #
    def load(self, fileName, mustExist):
        if None == fileName or 0 == len(fileName):
            # ???
            raise sudokuError("No valid filename")
    
        self.gridFileName_ = fileName
        
        # Open and read the file
        #
        try:
            file = open(fileName)
        except FileNotFoundError:
            if True == mustExist:
                raise sudokuError("The file '" + fileName + "' doesn't exist")
            else:
                print("Creation of '" + fileName + "'")
                return
            
        pt = pointer(gameMode = False)

        # Reading the lines
        for line in file: 

            # Not a comment !
            if line[0] != self.FILE_COMMENTS :
                # remove EOL
                if line[len(line) - 1] == "\n":
                    line = line[:len(line) - 1]

                values = line.split(self.VALUE_SEPARATOR)

                if not pointer.ROW_COUNT == len(values):
                    raise sudokuError("Invalid format for line n° " + str(pt.line()+1)+ " - " + str(len(values)) + " values")

                for val in values:
                    if val.isnumeric():

                        # in [0,9] ?
                        nVal = int(val)
                        if nVal < 0 or nVal > pointer.LINE_COUNT:
                            raise sudokuError("Error : le value (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ") isn't valid : " + val)

                        #  Value "0" for empty element
                        if nVal > 0:
                            # Check the line
                            if False == self._checkLine(pt, nVal):
                                raise sudokuError("Line value error : value " + val + " can't be set in (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")

                            # Check the row
                            if False == self._checkRow(pt, nVal):
                                raise sudokuError("Row value error : value " + val + " can't be set in (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")

                            # Check the "small" square
                            if False == self._checkSquare(pt, nVal):
                                raise sudokuError("Square value error : value " + val + " can't be set in (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")
                            
                            # add the value
                            self.elements_[pt.line() * pointer.ROW_COUNT + pt.row()].setValue(nVal, True)
                    else:
                        if (len(val)):
                            raise sudokuError("Error : the value (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ") is not numeric : " + val)

                    # Next value
                    pt += 1

        file.close()

        self.outputs_.setGridName(self.gridFileName_)

    # Save the file
    #
    def save(self, genName = False, comments = None):
        
        if None == self.gridFileName_:
            return False
        
        fileName = self.gridFileName_
        if genName :
            fileName += self.FILE_EXPORT_EXTENSION
        
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
            for lIndex in range(pointer.LINE_COUNT) :
                line = ""
                for _ in range(pointer.ROW_COUNT):
                    el = self.elements_[pt.index()]
                    line+=str(0 if el.isEmpty() else el.value())
                    line+=self.VALUE_SEPARATOR
                    pt+=1
                
                # add separator
                line = line[:len(line) - 1]
                if lIndex < (pointer.LINE_COUNT -1):
                    line+="\n"
                
                file.write(line)
            
            file.close()
            return True
        except ModuleNotFoundError:
            raise sudokuError("io error while writing in " + self.gridFileName_)

    # Edit / modify the grid
    #
    #   Returns a boolean : grid saved ?
    #
    def edit(self):
        # Can we edit this grid
        if None == self.outputs_ or False == self.outputs_.allowEdition():
            return False

        # Edition
        #
        valid = False
        cont = True
        currentPos = pointer(gameMode=False)      # current position
        prevPos = None                            # previous pos (if erase needed)
        
        while cont:
            # if sel. changed, erase previously selected element
            if not None == prevPos:
                self.outputs_.drawSingleElement(prevPos.row(), prevPos.line(), self.elements_[prevPos.index()].value(), True, self.outputs_.BK_COLOUR, self.outputs_.TXT_COLOUR)
            
            # Hilight the new value
            self.outputs_.drawSingleElement(currentPos.row(), currentPos.line(), self.elements_[currentPos.index()].value(), True, self.outputs_.SEL_BK_COLOUR, self.outputs_.SEL_TXT_COLOUR)
            self.outputs_.update()
            prevPos = pointer(currentPos)

            # Wait for a keyboard event
            #
            event = self.outputs_.waitForEvent(self.elements_, allEvents = True)
            
            # Change the cursor's position
            #
            if event.type == self.outputs_.EVT_KEYDOWN:
                if self.outputs_.MOVE_LEFT == event.key:
                    #position -= 1
                    currentPos.decRow()
                else:
                    if self.outputs_.MOVE_RIGHT == event.key:
                        #position += 1
                        currentPos.incRow()
                    else:
                        if self.outputs_.MOVE_UP == event.key:
                            currentPos.decLine()
                        else:
                            if self.outputs_.MOVE_DOWN == event.key:
                                currentPos.incLine()
                            else:
                                # Change the current value
                                #
                                if self.outputs_.VALUE_DEC == event.key:
                                    val = self.elements_[currentPos.index()].value()
                                    if None == val : 
                                        val = 0
                                    
                                    newVal = self._findPreviousValue(currentPos, val)
                                    if not newVal == val:
                                        self.elements_[currentPos.index()].setValue(newVal, True, True)
                                        prevPos = None
                                else:
                                    if self.outputs_.VALUE_INC == event.key:
                                        val = self.elements_[currentPos.index()].value()
                                        if None == val : 
                                            val = 0
                                        
                                        newVal = self._findNextValue(currentPos, val)
                                        if not newVal == val:
                                            self.elements_[currentPos.index()].setValue(newVal, True, True)
                                            prevPos = None
                                    else:
                                        # Cancel
                                        if self.outputs_.EDIT_CANCEL == event.key:
                                            cont = False
                                            valid = False
                                        else:
                                            # Save current grid
                                            if self.outputs_.EDIT_QUIT_AND_SAVE == event.key:
                                                cont = False
                                                valid = True
            elif event.type == self.outputs_.EVT_QUIT:
                # Quits
                cont = False
                valid = False

        # Saves changes or exit
        return self.save() if True == valid else False
    
    # Try to solve the grid
    #
    #   return a tuple (#attempts, duration in s.)
    #
    def resolve(self):
        
        # for stats
        self.attempts_ = 0
        self.start_ = time.time()
            
        # Let's go
        try:
            self._resolve()
        except reachedEndOfList:
            # Find a solution !!!
            return (self.attempts_, time.time() - self.start_) 
        
        # ???
        return (0,0)

    # Get the list of possible values at a given position
    #
    def getValues(self, position):
        values = []

        for value in range(pointer.VALUE_MIN, pointer.VALUE_MAX):
            if self._checkValue(position, value):
                # This value can be used
                values.append(value)
        
        # return the list
        return values

    #
    # Internal methods
    #

    # Empties the grid
    #
    def _emptyGrid(self):
        for element in self.elements_:
            element.empty()

    # Solve the grid (internal method without exceptions handling)
    #
    def _resolve(self):

        candidate = 0
        position = pointer(gameMode = True)
        position = self._findFirstEmptyPos(position)

        # All the elements "before" the current position are set with possible/allowed values
        # we'll try to put the "candidate" value at the current position
        while True :

            candidate +=1

            if candidate > pointer.VALUE_MAX:
                # No possible value found at this position
                # we'll have to go backward, to the last value setted
                position = self._previousPos(position)

                self.outputs_.updateGrid(self.elements_, position)

                # candidate value = prev. value (incremented at next occurence)
                candidate = self.elements_[position.index()].empty()
            else :
                # Try to put the "candidate" value at current position
                #
                if True == self._checkValue(position, candidate):
                    # possible !!!
                    self.attempts_ += 1

                    self.elements_[position.index()].setValue(candidate)
                    self.outputs_.updateGrid(self.elements_, position)
                    
                    # On avance jusqu'à la position vide suivante
                    position = self._findFirstEmptyPos(position)
                    
                    # At the next pos., we alawyas try the lowest possible value
                    candidate = 0 


    # Can we put the value at the current position ?
    #
    def _checkValue(self, position, value):
        return self._checkLine(position, value) and self._checkRow(position, value) and self._checkSquare(position, value)

    #   => in the line ?
    def _checkLine(self, position, value):
        idFirst = position.line() * pointer.ROW_COUNT 
        for tIndex in range(pointer.ROW_COUNT):
            if self.elements_[tIndex + idFirst].value() == value:
                return False
        # yes
        return True

    #  => in the row ?
    def _checkRow(self, position, value):
        idFirst = position.row()
        for tIndex in range(pointer.LINE_COUNT):
            if self.elements_[tIndex * pointer.ROW_COUNT + idFirst].value() == value:
                return False
        # yes
        return True

    #  => in the "small" square ?
    def _checkSquare(self, position, value):
        tIndex = self.squareIndex_[position.squareID()]      
        for _ in range (3):
            for tRow in range(3):
                if self.elements_[tIndex + tRow].value() == value:
                    return False
            tIndex+=pointer.ROW_COUNT
        # yes
        return True

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

    # Reurns to the previous position 
    #
    #   Returns a pointer to the found position
    #   An IndexError excpetion is raised when the pointer is out of the grid (index -1)
    #   No soluce for the grid
    # 
    def _previousPos(self, current):
        newPos = pointer(current)

        self.elements_[newPos.index()].empty()
        newPos -= 1

        # while self.elements_[newPos.index()].isOriginal():
        
        # Don't touch "Original" nor "Obvious" values
        while self.elements_[newPos.index()].isChangeable():
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

# EOF