# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver and ownColour objects
#                       - GUI for sudoku solver
#
import copy
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

# editSel - Edition and selection inf.
#
class editStatus:
    # Edition status
    #
    EDIT_NO_EDITION:int = statusbits.STATUS_NONE
    EDIT_CONTINUE:int = 2
    EDIT_MODIFIED:int = 4  # The sudoku has been modified (at least once)
    EDIT_STOP:int = 8  # Stop edition
    EDIT_ESCAPE:int = 16  # Escape edition
    EDIT_ESCAPED:int = EDIT_STOP | EDIT_ESCAPE
    EDIT_NO_REDRAW:int = 32  # don't redraw at previous pos value

    def __init__(self):
        self.status_ : statusbits.statusBits = statusbits.statusBits(self.EDIT_NO_EDITION)
        self.currentPos_ : pointer = pointer(0)
        self.prevPos_ : pointer | None = None
        self.blink_ : bool = False

    def clear(self, status : int = EDIT_NO_EDITION, editable:bool = False):
        self.status_.set(status)
        self.currentPos_.clear(False)
        self.prevPos_ = None
        self.blink_ = False
        self.editable = editable

    def move(self):
        self.prevPos_ = copy.deepcopy(self.currentPos_)
        self.status_.remove(self.EDIT_NO_REDRAW)

    # Blinking effect
    @property
    def blink(self)->bool:
        return self.blink_
    @blink.setter
    def blink(self, set : bool = True):
        self.blink_ = set
    def changeBlink(self)->bool:
        self.blink_ = not self.blink_
        return self.blink_

    # Value modified ?
    @property
    def modified(self)->bool:
        return self.status_.isSet(self.EDIT_MODIFIED)

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

    #
    #  key codes
    #

    # Change pos.
    KEY_MOVE_LEFT:int = 0
    KEY_MOVE_RIGHT:int = 0
    KEY_MOVE_UP:int = 0
    KEY_MOVE_DOWN:int = 0

    # Change element value
    KEY_REMOVE_VALUE:int = 0
    KEY_REMOVE_VALUE_BIS:int = 0

    KEY_VALUE_DEC:int = 0
    KEY_VALUE_INC:int = 0

    # Set value
    KEY_VALUE_1:int = 0
    KEY_VALUE_9:int = 0

    KEY_VALUE_KPAD_1:int = 0
    KEY_VALUE_KPAD_9:int = 0

    KEY_ENTER:int = 0

    EDIT_CANCEL:int = 0


    # Colours' ID
    #
    class ColourID(IntEnum):
        ID_BORDER = 0
        ID_BK = auto()
        ID_BK_FILENAME = auto()
        ID_TXT = auto()
        ID_HILITE = auto()
        ID_HILITE_TXT = ID_TXT
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
        self.edition_ : editStatus = editStatus()

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
        #self.colours_.append(ownColour(HILITE_COLOUR))
        self.colours_.append(ownColour(SEL_BK_COLOUR))
        self.colours_.append(ownColour(SEL_TXT_COLOUR))

        # self.params_.center = True

    @property
    def initialized(self)->bool:
        return self.initDone_
    @initialized.setter
    def initialized(self, newVal : bool):
        self.initDone_ = newVal

    # Filename
    @property
    def filename(self)->str:
        return self.params_.fileName_
    @filename.setter
    def filename(self, newVal : str):
        self.params_.fileName_ = newVal

    # Set/change the current array's filename
    #
    def setFilename(self, fileName:str, create:bool = False):
        # the file must exists
        if False == create and False == os.path.isfile(fileName):
            raise sudokuError(f"{fileName} is not a file or does not exist")
        self.filename = fileName

    #
    # Theses methods MUST be overriden
    #

    # GUI initialization
    #
    def initialize(self):
        # Default dimensions
        self.width_ = ROW_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_W + GUIConsts.STATS_FRAME_WIDTH
        self.height_ = LINE_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_H
        self.offsets_ = (GUIConsts.DELTA_W, GUIConsts.DELTA_H)
        self.extSquareWidth_ = GUIConsts.SQUARE_SIDE
        self.intSquareWidth_ = GUIConsts.SQUARE_SIDE - 2 * GUIConsts.EXT_BORDER_THICK
        self.fontsize_ = GUIConsts.ELT_FONT_SIZE

        self._draw_convertColours() # Convert colours

    # Start drawings / UI
    #
    def startUI(self):
        pass

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
            self.setFilename(fileName)
            self.draw(redrawBackground=True)

        return True

    #
    # Drawing in the client area
    #

    # Draw the whole array
    #
    #   elements :  array of elements to draw or None.
    #               if None, current sudoku will be drawn
    #
    def draw(self, elements : list[element] | None = None, redrawBackground : bool = False):
        if elements is None :
            elements = self.sudoku_.elements_

        if len(elements) > 0 :
            self._draw_startUp()

            if redrawBackground:
                self._draw_background()

            position : pointer = pointer(game = False)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    currentElement = elements[position.index()]
                    self._draw_singleElement(
                        row, line,
                        currentElement.num,
                        self.ColourID.ID_BK,
                        self.ColourID.ID_HILITE if currentElement.isOriginal() else self.ColourID.ID_OBVIOUS if currentElement.isObvious() else self.ColourID.ID_TXT
                    )

                    # next element ...
                    position+=1

            self._draw_end()

    def _draw_startUp(self):
        pass

    # Update the whole window
    #
    def _draw_update(self):
        self.draw(redrawBackground=True)

    def _draw_end(self):
        pass

    # Draw selected element (on edit mode)
    #
    def _draw_elementSelected(self, hilite : bool = True):
        currentElement : element =self.sudoku_.elements_[self.edition_.currentPos_.index()]
        value : int | None = currentElement.num
        self._draw_startUp()
        self._draw_singleElement(
            self.edition_.currentPos_.row(),
            self.edition_.currentPos_.line(),
            value,
            self.ColourID.ID_SEL_BK if hilite else self.ColourID.ID_BK,
            self.ColourID.ID_HILITE if currentElement.isOriginal() else self.ColourID.ID_OBVIOUS if currentElement.isObvious() else self.ColourID.ID_TXT)

    # Draw/erase a single element and its background
    #
    def _draw_singleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int):
        pass

    # Draw background, frames and borders
    #
    def _draw_background(self):
        pass

    # The window's size has changed
    #
    def _draw_newClientSize(self, newWidth:int, newHeight:int):
        self.width_ = newWidth
        self.height_ = newHeight

        # Compute new square sizes
        squareW = math.floor((newWidth - 2 * GUIConsts.DELTA_W - GUIConsts.STATS_FRAME_WIDTH) / ROW_COUNT)
        squareH = math.floor((newHeight - 2 * GUIConsts.DELTA_H) / LINE_COUNT)

        if squareW < GUIConsts.SQUARE_MIN or squareH < GUIConsts.SQUARE_MIN :
            self.extSquareWidth_ = GUIConsts.SQUARE_MIN

        # Use the smallest !
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * GUIConsts.EXT_BORDER_THICK

        if self.params_.center :
            self.offsets_ = (math.floor((self.width_ - (self.extSquareWidth_ * ROW_COUNT)) / 2),
                math.floor((self.height_ - self.extSquareWidth_ * LINE_COUNT) / 2))
        else:
            self.offsets_ = (GUIConsts.DELTA_W, GUIConsts.DELTA_H)  # aligned with top left corner

        # font size in pixels
        self.fontSize_ = int(GUIConsts.ELT_FONT_SIZE * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE)


    # Mouse position : screen -> array coordinates
    #
    def _mouse_translatePosition(self, pos : tuple[int,int])->tuple[int, int]:
        if pos[1] > self.offsets_[1] :
            x : int = int((pos[0] - GUIConsts.EXT_BORDER_THICK - self.offsets_[0]) / self.extSquareWidth_)
            y : int = int((pos[1] - GUIConsts.EXT_BORDER_THICK - self.offsets_[1]) / self.extSquareWidth_)
            return (x,y)
        return (-1,-1)

    # End drawings
    #
    def end(self):
        pass

    # Convert colour objects from ownColour to pygameColor
    #
    def _draw_convertColours(self):
        pass

    #
    #  Other "shared" methods
    #

    # Find all the obvious values
    #
    #   return a boolean : found value(s) ?
    #
    def findObviousValues(self)->bool:
        self.stats_.clear()
        found : int = 0
        start : float = time.time()
        values = 1
        while 0 < values:
            values = self.sudoku_.findObviousValues()
            found += values

        if found>0:
            self.stats_.obvValues_ = found
            self.stats_.obvDuration_ = time.time() - start
            return True

        return False

    # Resolve current sudoku using local parameters
    #
    # returns found a solution ?
    def resolve(self)->bool:
        found:bool = False
        self.stats_.clear(False)

        # for stats
        start : float = time.time()

        # Let's go
        match self.params_.progressMode_ :
            case self.params_.PROGRESS_MULTITHREADED:
                found = self._resolve_MultiThreaded()

            case self.params_.PROGRESS_SHOW_SAME_THREAD:
                found = self._resolve_AndDisplay()

            case _:
                found = self._resolve_SingleThreaded()

        if found:
            self.stats_.bruteAttempts_ = self.sudoku_.attempts
            self.stats_.bruteDuration_ = time.time() - start

        # Finished (anyway)
        return found

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

    # Start edition mode
    #
    def _edit_start(self):
        pass

    # End of edition mode
    #
    def _edit_stop(self):
        pass

    # Update array during edition
    #
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        self._draw_startUp()

        if prevPos is not None :
            prevElement : element = self.sudoku_.elements_[prevPos.index()]
            # if sel. changed, erase previously selected element
            self._draw_singleElement(
                prevPos.row(),
                prevPos.line(),
                self.sudoku_.elements_[prevPos.index()].num,
                self.ColourID.ID_BK,
                self.ColourID.ID_HILITE if prevElement.isOriginal() else self.ColourID.ID_OBVIOUS if prevElement.isObvious() else self.ColourID.ID_TXT,
            )

        # Hilight the new value
        currentElement : element =self.sudoku_.elements_[self.edition_.currentPos_.index()]
        self._draw_singleElement(
            currentPos.row(),
            currentPos.line(),
            self.sudoku_.elements_[currentPos.index()].num,
            self.ColourID.ID_SEL_BK,
            self.ColourID.ID_HILITE if currentElement.isOriginal() else self.ColourID.ID_OBVIOUS if currentElement.isObvious() else self.ColourID.ID_TXT
        )

        self._draw_end()

    # (try to) set a value
    #
    def _edit_setValue(self, val: int):
        if self.sudoku_.checkValue(self.edition_.currentPos_, val):
            self.sudoku_.elements_[self.edition_.currentPos_.index()].setValue(val, element.STATUS_ORIGINAL, True)
            self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)

    # Decrease value
    #
    def _edit_decValue(self):
        val : int | None = self.sudoku_.elements_[self.edition_.currentPos_.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findPreviousValue(self.edition_.currentPos_, val)
        if newVal != val:
            self.sudoku_.elements_[self.edition_.currentPos_.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)

    # Inc value
    #
    def _edit_incValue(self):
        val : int | None = self.sudoku_.elements_[self.edition_.currentPos_.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findNextValue(self.edition_.currentPos_, val)
        if newVal != val:
            self.sudoku_.elements_[self.edition_.currentPos_.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)

    # Remove current value
    #
    def _edit_removeValue(self):
        self.sudoku_.elements_[self.edition_.currentPos_.index()].setValue(0, element.STATUS_ORIGINAL, True)
        self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)

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
