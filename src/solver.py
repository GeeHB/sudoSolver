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
    COLOUR_BK,
    COLOUR_BK_FILENAME,
    COLOUR_BLUE,
    COLOUR_BORDER,
    COLOUR_GREEN,
    COLOUR_ORIGINAL,
    COLOUR_RED,
    COLOUR_SEL_BK,
    COLOUR_SEL_TXT,
    COLOUR_TXT,
    COLOUR_YELLOW,
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


# A "previous" value in the array
#
class prevValue:
    def __init__(self, index:int, value:int | None):
        self.index_ = index
        self.value_ = value if value is not None else 0
    def __repr__(self)->str:
        return f"(Id:{self.index_} - val:{self.value_})"

# ownColour - General and portable colour definition
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
    EDIT_MODE_CREATION:int = 1
    EDIT_MODE_RESOLUTION:int = 2
    EDIT_CONTINUE:int = 4
    EDIT_MODIFIED:int = 8  # The sudoku has been modified (at least once)
    EDIT_STOP:int = 16  # Stop edition
    EDIT_ESCAPE:int = 32  # Escape edition
    EDIT_ESCAPED:int = EDIT_STOP | EDIT_ESCAPE
    EDIT_NO_REDRAW:int = 64  # don't redraw at previous pos value

    def __init__(self):
        self.status_ : statusbits.statusBits = statusbits.statusBits(self.EDIT_NO_EDITION)
        self.currentPos_ : pointer = pointer(0)
        self.prevPos_ : pointer | None = None
        self.blink_ : bool = False

    def clear(self, status : int = EDIT_NO_EDITION):
        self.status_.set(status)
        self.currentPos_.clear(False)
        self.prevPos_ = None
        self.blink_ = False

    def move(self):
        self.prevPos_ = copy.deepcopy(self.currentPos_)
        self.status_.remove(self.EDIT_NO_REDRAW)

    # Edition modes
    #

    # in creation mode ?
    @property
    def creating(self)->bool:
        return self.status_.isSet(self.EDIT_MODE_CREATION)
    @creating.setter
    def creating(self, set : bool = True):
        if set: self.manualSolving = False
        self.status_.set(self.EDIT_MODE_CREATION, set)

    # or in manual solving mode ?
    @property
    def manualSolving(self)->bool:
        return self.status_.isSet(self.EDIT_MODE_RESOLUTION)
    @manualSolving.setter
    def manualSolving(self, set : bool = True):
        if set : self.creating = False
        self.status_.set(self.EDIT_MODE_RESOLUTION, set)

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
        ID_ORIGINAL_TXT = auto()
        ID_OBVIOUS_TXT = ID_BORDER
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
        self.offsets_: tuple[int,int] = (0,0)
        self.width_:int = 0        # Window's dimensions
        self.height_: int = 0
        self.intSquareWidth_:int = 0        # Internal dims of an element
        self.extSquareWidth_:int = 0        # Ext. dims
        self.fontsize_: int = 0
        self.tagWidth_:int = 0

        self.prevValues_: list[prevValue] = []   # List of prev. values during edition

        # Default colours
        #
        #   A list of  colours
        #
        self.colours_ : list[ownColour] = []

        # for array and window
        self.colours_.append(ownColour(COLOUR_BORDER))
        self.colours_.append(ownColour(COLOUR_BK))
        self.colours_.append(ownColour(COLOUR_BK_FILENAME))
        self.colours_.append(ownColour(COLOUR_TXT))
        self.colours_.append(ownColour(COLOUR_ORIGINAL))
        #self.colours_.append(ownColour(COLOUR_ORIGINAL))
        self.colours_.append(ownColour(COLOUR_SEL_BK))
        self.colours_.append(ownColour(COLOUR_SEL_TXT))

        # for hyptohesis
        self.hypColoursStart_:int =len(self.colours_) - 1
        self.colours_.append(ownColour(COLOUR_YELLOW))
        self.colours_.append(ownColour(COLOUR_BLUE))
        self.colours_.append(ownColour(COLOUR_GREEN))
        self.colours_.append(ownColour(COLOUR_RED))


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
        #return self.params_.fileName_
        return self.sudoku_.filename
    @filename.setter
    def filename(self, newVal : str):
        self.params_.fileName_ = newVal # BUG ? : should be useless
        self.sudoku_.filename = newVal

    # Set/change the current array's filename
    #
    def setFilename(self, fileName:str, create:bool = False):
        # the file must exists
        if False == create and False == os.path.isfile(fileName):
            raise sudokuError(f"solver::setFilename - {fileName} is not a file or does not exist")
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

        #self.setFilename(fileName)

        if redraw:
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
        #print(f"Non-empty values : {self.sudoku_.count_}")
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
                    bk, txt = self._draw_elementTxtColours(position.index(), False)
                    self._draw_singleElement(
                        row, line,
                        currentElement.num,
                        bk, txt,
                        currentElement.hypothesis,
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
    def _draw_selectedElement(self, selected : bool = True):
        index:int = self.edition_.currentPos_.index()
        currentElement : element =self.sudoku_.elements_[index]
        value : int | None = currentElement.num
        self._draw_startUp()

        bk, txt = self._draw_elementTxtColours(index, selected)
        self._draw_singleElement(
            self.edition_.currentPos_.row(),
            self.edition_.currentPos_.line(),
            value,
            bk, txt,
            currentElement.hypothesis
        )

    # Draw/erase a single element and its background
    #
    def _draw_singleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int, hypColourID:int):
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

        # tag dims.
        self.tagWidth_ = int(GUIConsts.TAG_MIN_SIZE * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE)
        if self.tagWidth_ % 2 != 0:
            self.tagWidth_+=1
        self.tagWidth_ = min(self.tagWidth_, GUIConsts.TAG_MAX_SIZE)

    # Get elementss text and bk colours for edition or creation
    #
    #  @pos : Element's position
    #  @sekected : Element is selected ?
    #
    #  @return : Tuple(bk Colour, txt Colour)
    def _draw_elementTxtColours(self, pos: int, selected:bool = False)->tuple[int,int]:
        bkColour:int = self.ColourID.ID_SEL_BK if selected else self.ColourID.ID_BK
        if self.edition_.creating:
            return bkColour, self.ColourID.ID_ORIGINAL_TXT   # always use "original" colour

        if self.sudoku_.elements_[pos].isObvious():
            return bkColour, self.ColourID.ID_OBVIOUS_TXT
        else:
            if self.sudoku_.elements_[pos].isOriginal():
                return bkColour, self.ColourID.ID_ORIGINAL_TXT

        return bkColour, self.ColourID.ID_SEL_TXT if selected else self.ColourID.ID_TXT

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
            values = self.sudoku_.obvious_findValues()
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
    def _edit_start(self, initPos:bool = True):
        self.prevValues_.clear()        # Nothing to undo or cancel

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
            bk, txt = self._draw_elementTxtColours(prevPos.index_, False)

            # if sel. changed, erase previously selected element
            self._draw_singleElement(
                prevPos.row(),
                prevPos.line(),
                self.sudoku_.elements_[prevPos.index()].num,
                bk, txt,
                prevElement.hypothesis
            )

        # Hilight the new value
        index: int = self.edition_.currentPos_.index()
        currentElement : element = self.sudoku_.elements_[index]
        bk, txt = self._draw_elementTxtColours(index, True)
        self._draw_singleElement(
            currentPos.row(),
            currentPos.line(),
            self.sudoku_.elements_[currentPos.index()].num,
            bk, txt,
            currentElement.hypothesis
        )

        self._draw_end()

    # (try to) set a value
    #
    #  @return : Index of modified item or -1
    #
    def _edit_setValue(self, val: int)->int:
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_.elements_[index].isChangeable():
            return -1

        if self.sudoku_.checkValue(self.edition_.currentPos_, val):
            return self._edit_setValueEx(val, id= index)

        return -1

    def _edit_setValueEx(self, val: int, id:int = -1, keep:bool = True)->int:
        index:int = id if id != -1 else self.edition_.currentPos_.index()
        if keep:
            self.prevValues_.append(prevValue(index, self.sudoku_.elements_[index].num))
        #self.sudoku_.elements_[index].setValue(val, element.STATUS_ORIGINAL, True)
        self.sudoku_.modifyAt(pointer(index,False), val,
            (element.STATUS_ORIGINAL if self.edition_.creating else 0) | element.STATUS_SET)
        self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)
        return index

    # Decrease value
    #
    def _edit_decValue(self):
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_.elements_[index].isChangeable():
            return

        val : int | None = self.sudoku_.elements_[index].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findPreviousValue(self.edition_.currentPos_, val)
        if newVal != val:
            self._edit_setValueEx(newVal, index)

    # Inc value
    #
    def _edit_incValue(self):
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_.elements_[index].isChangeable():
            return
        val : int | None = self.sudoku_.elements_[index].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findNextValue(self.edition_.currentPos_, val)
        if newVal != val:
            self._edit_setValueEx(newVal, index)

    # Remove current value
    #
    def _edit_removeValue(self):
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_.elements_[index].isChangeable():
            return

        self.sudoku_.clearAt(self.edition_.currentPos_.index(), True)

    # Undo
    #
    #  Returns position of modified element or -1 on error
    def _edit_undo(self)->int:
        if len(self.prevValues_) > 0:
            prev:prevValue = self.prevValues_.pop()
            if prev.value_ > 0 :
                self._edit_setValueEx(prev.value_, prev.index_, keep=False)
            else:
                self.sudoku_.clearAt(prev.index_, True)
            return prev.index_
        return -1

    # Cancel current edition process (and whole changes)
    #
    def _edit_cancel(self)->bool:
        if len(self.prevValues_) == 0:
            return False

        for val in reversed(self.prevValues_):
            if val.value_ > 0:
                self.sudoku_.elements_[val.index_].setValue(val.value_, element.STATUS_ORIGINAL, True)
            else:
                self.sudoku_.elements_[val.index_].empty(True)

        self.prevValues_.clear()
        return True


    #
    # Resolution
    #

    # Single-threaded mode
    #
    # returns True if a solution has been founded
    def _resolve_SingleThreaded(self)->bool:
        try:
            self.sudoku_.resolve_singleThreaded()
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
        for _ in self.sudoku_.resolve_singleThreadGenerator() :
            self.draw()

        return self.sudoku_.found

    # Multi-threaded mode
    #
    # returns True if a solution has been founded
    def _resolve_MultiThreaded(self)->bool:
        self.sudoku_.resolve_multiThreaded() # start resolution thread
        while self.sudoku_.is_alive():
            self.draw(redrawBackground=False)     # redraw sudoku while searching for a solution

        return self.sudoku_.found

# EOF
