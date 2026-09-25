# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver and ownColour objects
#                       - GUI for sudoku solver
#
import math
import os
import time
from enum import IntEnum, auto
from typing import Any

import GUIConsts
from element import element
from GUIConsts import (
    BK_COLOUR,
    BK_COLOUR_FILENAME,
    BORDER_COLOUR,
    HILITE_COLOUR,
    SEL_BK_COLOUR,
    SEL_TXT_COLOUR,
    TXT_COLOUR,
)
from options import (
    options,
    stats,
)
from ownExceptions import reachedEndOfList, sudokuError
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
    pointer,
)
from sharedTools import (
    statusbits,
)
from sudoku import sudoku

# Edition status
#
EDIT_CONTINUE:int = statusbits.STATUS_NONE
EDIT_MODIFIED:int = 1  # The sudoku has been modified (at least once)
EDIT_STOP:int = 2  # Stop edition
EDIT_ESCAPE:int = 4  # Escape edition
EDIT_ESCAPED:int = EDIT_STOP | EDIT_ESCAPE
EDIT_NOREDRAW:int = 8  # don't redraw at previous pos value

# colour - General and portable colour definition
#
class ownColour:
    r : int
    g : int
    b : int
    a : int

    def __init__(self, rgb : tuple[int,int,int] | None, alpha : int | None = None):
        if rgb is not None:
            self.r = rgb[0]
            self.g = rgb[1]
            self.b = rgb[2]
        self.a = alpha if alpha is not None else 255
        self.other : Any = None

# solverApp - Abstract class for application
#
class solverApp:
    # Constructor
    #
    def __init__(self, params : options):
        pass

    # GUI initialization
    #
    def initialize(self):
        pass

    # Start drawings / UI
    #
    def start(self):
        pass

    # End drawings
    #
    def end(self):
        pass

# solver - Abstract class for GUI sudoku solvers
#
class solver:
    # Colours' ID
    #
    class ColourID(IntEnum):
        ID_BORDER = 0
        ID_BK = auto()
        ID_BK_FILENAME = auto()
        ID_TXT = auto()
        ID_HILITE = auto()
        ID_OBVIOUS = ID_BORDER
        ID_SEL_BK = auto()
        ID_SEL_TXT = auto()

    # Constructor
    #
    def __init__(self, params : options):
        self.initDone_ : bool = False
        self.params_ : options = params
        self.sudoku_ : sudoku = sudoku()    # First, the array is empty
        self.stats_ : stats = stats()
        self.editStatus_:statusbits.statusBits = statusbits.statusBits(EDIT_CONTINUE)

        # Dimensions
        #
        self.offsets_ : tuple[int,int] = (0,0)
        self.width_ :int = 0        # Window's dimensions
        self.height_ : int = 0
        self.intSquareWidth_ :int = 0        # Internal dims of an element
        self.extSquareWidth_ :int = 0        # Ext. dims
        self.fontsize_ : int = 0

        # Default colours
        #
        #   A list of  colours
        #
        self.colours_ : list[ownColour] = []
        self.colours_.append(ownColour(BORDER_COLOUR))
        self.colours_.append(ownColour(BK_COLOUR))
        self.colours_.append(ownColour(BK_COLOUR_FILENAME))
        self.colours_.append(ownColour(TXT_COLOUR))
        self.colours_.append(ownColour(HILITE_COLOUR))
        self.colours_.append(ownColour(SEL_BK_COLOUR))
        self.colours_.append(ownColour(SEL_TXT_COLOUR))

        self.params_.center = False

    @property
    def initialized(self)->bool:
        return self.initDone_
    @initialized.setter
    def initialized(self, newVal : bool):
        self.initDone_ = newVal

    # Filename
    @property
    def filename(self)->str|None:
        return self.params_.fileName_
    @filename.setter
    def filename(self, newVal : str):
        self.params_.fileName_ = newVal

    #
    # Theses methods MUST be overriden
    #

    # GUI initialization
    #
    def initialize(self):
        # Default dimensions
        self.width_ = ROW_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_W + GUIConsts.STATS_FRAME_WIDTH
        self.height_ = GUIConsts.MENUBAR_HEIGHT + LINE_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_H
        self.extSquareWidth_ = GUIConsts.SQUARE_SIDE
        self.intSquareWidth_ = GUIConsts.SQUARE_SIDE - 2 * GUIConsts.EXT_BORDER_THICK
        self.fontsize_ = GUIConsts.ELT_FONT_SIZE

        self.convertColours() # Convert colours

    # Start drawings / UI
    #
    def startUI(self):
        pass

    # Set/change the current array's filename
    #
    def setFileName(self, fileName:str, create:bool = False):
        # the file must exists
        if False == create and False == os.path.isfile(fileName):
            raise sudokuError(fileName +  " is not a file")

        self.filename = fileName


    # Load a sudoku stored in a file
    #
    #   return True if sudoku has been successfully loaded
    #
    def fromFile(self, fileName : str, redraw:bool=True) -> bool:
        self.sudoku_.empty()

        try:
            self.sudoku_.load(fileName, True, False)
        except UnicodeDecodeError:
            return False
        except sudokuError as se:
            print(f"Sudoku Error : {se.message_}")
            return False

        if redraw:
            self.setFileName(fileName)
            self.draw(redrawBackground=True)

        return True

    #
    # Drawing in the client area
    #

    def _display_StartUp(self):
        pass

    def _display_End(self):
        pass

    # Draw the whole array
    #
    #   elements :  array of elements to draw or None.
    #               if None, current sudoku will be drawn
    #
    def draw(self, elements : list[element] | None = None, redrawBackground : bool = False):
        self._display_StartUp()

        if redrawBackground:
            self.drawBackground()

        position : pointer = pointer(gameMode = False)
        if elements is None :
            elements = self.sudoku_.elements_

        for line in range(LINE_COUNT):
            for row in range(ROW_COUNT):
                currentElement = elements[position.index()]
                value : int | None = currentElement.num
                self.drawSingleElement(
                    row, line,
                    value,
                    self.ColourID.ID_BK,
                    self.ColourID.ID_HILITE if currentElement.isOriginal() else self.ColourID.ID_OBVIOUS if currentElement.isObvious() else self.ColourID.ID_TXT
                )

                # next element ...
                position+=1

        self.update()
        self._display_End()

    # The window's size has changed
    #
    def newWindowSize(self, newWidth:int, newHeight:int):
        self.width_ = newWidth
        self.height_ = newHeight

        # Compute new square sizes
        squareW = math.floor((newWidth - 2 * GUIConsts.DELTA_W - GUIConsts.STATS_FRAME_WIDTH) / ROW_COUNT)
        squareH = math.floor((newHeight - GUIConsts.MENUBAR_HEIGHT - 2 * GUIConsts.DELTA_H) / LINE_COUNT)

        if squareW < GUIConsts.SQUARE_MIN or squareH < GUIConsts.SQUARE_MIN :
            self.extSquareWidth_ = GUIConsts.SQUARE_MIN

        # Use the smallest !
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * GUIConsts.EXT_BORDER_THICK

        if self.params_.center :
            self.offsets_ = (math.floor((self.width_ - (self.extSquareWidth_ * ROW_COUNT + 2 * GUIConsts.DELTA_W + GUIConsts.STATS_FRAME_WIDTH)) / 2),
                GUIConsts.MENUBAR_HEIGHT + math.floor((self.height_ - (self.extSquareWidth_ * LINE_COUNT + 2 * GUIConsts.DELTA_H)) / 2))
        else:
            self.offsets_ = (0,0)

        # font size in pixels
        self.fontSize_ = int(GUIConsts.ELT_FONT_SIZE * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE)


    # Mouse position : screen -> array coordinates
    #
    def mousePosition(self, pos : tuple[int,int])->tuple[int, int]:
        x : int = int((pos[0] - GUIConsts.EXT_BORDER_THICK - GUIConsts.DELTA_W - self.offsets_[0]) / self.extSquareWidth_)
        y : int = int((pos[1] - GUIConsts.EXT_BORDER_THICK - GUIConsts.DELTA_W - self.offsets_[1]) / self.extSquareWidth_)
        return (x,y)

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int):
        pass

    # Draw background, frames and borders
    #
    def drawBackground(self):
        pass

    # Update the whole window
    #
    def update(self):
        pass

    # End drawings
    #
    def end(self):
        pass

    # Convert colour objects from ownColour to pygameColor
    #
    def convertColours(self):
        pass

    #
    #  Other "shared" methods
    #

    # Resolve current sudoku using local parameters
    #
    # returns the tuple (found a solution?, #attempts, duration)
    def resolve(self)->tuple[bool, int, float]:
        found = False

        # for stats
        start : float = time.time()
        end : float = 0.0

        # Let's go
        match self.params_.progressMode_ :
            case self.params_.PROGRESS_MULTITHREADED:
                found = self._resolve_MultiThreaded()

            case self.params_.PROGRESS_SHOW_SAME_THREAD:
                found = self._resolve_AndDisplay()

            case _:
                found = self._resolve_SingleThreaded()

        if found:
            end = time.time() - start

        # Finished (anyway)
        return (found, self.sudoku_.attempts, end)

    # Show resolution stats
    #
    #   Print stats on console (by default)
    #
    def showStats(self):
        print(f"\n\t- {self.filename}")

        # Found obvious values ?
        if self.params_.obviousValues:
            if self.stats_.obvValues_:
                print("\t- Found " + str(self.stats_.obvValues_) + " obvious value(s) in " + str(round(self.stats_.obvDuration_, 2)) + " second(s)")
            else:
                print("\t- No obvious value found")

        print("\t- Solved in " + str(round(self.stats_.bruteDuration_, 2)) + " second(s)")
        print("\t- " + str(self.stats_.bruteAttempts_) + " attempt(s)\n")

    #
    # Array edition
    #

    # Update array during edition
    #
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        self._display_StartUp()

        if prevPos is not None:
            # if sel. changed, erase previously selected element
            self.drawSingleElement(
                prevPos.row(),
                prevPos.line(),
                self.sudoku_.elements_[prevPos.index()].num,
                self.ColourID.ID_BK,
                self.ColourID.ID_HILITE,
            )

        # Hilight the new value
        self.drawSingleElement(
            currentPos.row(),
            currentPos.line(),
            self.sudoku_.elements_[currentPos.index()].num,
            self.ColourID.ID_SEL_BK,
            self.ColourID.ID_SEL_TXT,
        )

        self._display_End()


    # (try to) set a value
    #
    def _edit_setValue(self, pos: pointer, val: int):
        if self.sudoku_.checkValue(pos, val):
            self.sudoku_.elements_[pos.index()].setValue(val, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(EDIT_NOREDRAW | EDIT_MODIFIED)

    # Decrease value
    #
    def _edit_decValue(self, pos: pointer):
        val : int | None = self.sudoku_.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findPreviousValue(pos, val)
        if newVal != val:
            self.sudoku_.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(EDIT_NOREDRAW | EDIT_MODIFIED)

    # Inc value
    #
    def _edit_incValue(self, pos: pointer):
        val : int | None = self.sudoku_.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findNextValue(pos, val)
        if newVal != val:
            self.sudoku_.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(EDIT_NOREDRAW | EDIT_MODIFIED)

    # Remove current value
    #
    def _edit_removeValue(self, pos: pointer):
        self.sudoku_.elements_[pos.index()].setValue(0, element.STATUS_ORIGINAL, True)
        self.editStatus_.set(EDIT_NOREDRAW | EDIT_MODIFIED)

    #
    # Resolution
    #

    # Single-threaded mode
    #
    # returns True if a solution has been founded
    def _resolve_SingleThreaded(self)->bool:
        try:
            self.sudoku_.resolveSingleThreaded()
        except reachedEndOfList:
            # Found a solution !!!
            return True
        except IndexError:
            # No solution found
            return False

    # Single-threaded mode using a generator to display progression
    #
    # returns True if a solution has been founded
    def _resolve_AndDisplay(self)->bool:
        for _ in self.sudoku_.resolveGenerator() :
            self.draw()

        return self.sudoku_.found

    # Multi-threaded mode
    #
    # returns True if a solution has been founded
    def _resolve_MultiThreaded(self)->bool:
        self.sudoku_.resolveMultiThreaded() # start resolution thread
        while self.sudoku_.is_alive():
            self.draw(redrawBackground=False)     # redraw sudoku while searching for a solution

        return self.sudoku_.found
# EOF
