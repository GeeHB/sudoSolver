# coding=UTF-8
#
#   File        :   solver.py
#
#   Author      :   GeeHB
#
#   Description :   solver and ownColour objects
#                       - abstract classe for GUIed sudoku solver
#
import copy
import math
import os
import time
from enum import IntEnum

import GUIConsts
import GUITheme
from element import element
from options import (
    options,
    stats,
)
from ownExceptions import reachedEndOfList, sudokuError
from pointer import (
    ARRAY_SIZE,
    LINE_COUNT,
    ROW_COUNT,
    pointer,
)
from sharedTools import (
    statusbits,
)
from sudoku import sudoku


# A zone in the game area
#
class ownZone(IntEnum):
    ZONE_NOWHERE = 0
    ZONE_ARRAY = 1
    ZONE_HELP_MATRIX = 2

# A "previous" value in the array
#
class prevValue:
    def __init__(self, index:int, value:int | None):
        self.index_ = index
        self.value_ = value if value is not None else 0
    def __repr__(self)->str:
        return f"(Id:{self.index_} - val:{self.value_})"

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
        self.status_: statusbits.statusBits = statusbits.statusBits(self.EDIT_NO_EDITION)
        self.currentPos_: pointer = pointer(0)
        self.prevPos_: pointer | None = None
        self.selected_: bool = False

    def clear(self, status : int = EDIT_NO_EDITION):
        self.status_.set(status)
        self.currentPos_.clear(False)
        self.prevPos_ = None
        self.selected_ = False

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
    def creating(self, set:bool = True):
        if set: self.manualSolving = False
        self.status_.set(self.EDIT_MODE_CREATION, set)

    # or in manual solving mode ?
    @property
    def manualSolving(self)->bool:
        return self.status_.isSet(self.EDIT_MODE_RESOLUTION)
    @manualSolving.setter
    def manualSolving(self, set:bool = True):
        if set : self.creating = False
        self.status_.set(self.EDIT_MODE_RESOLUTION, set)

    # in edition (creation or solving) mode ?
    @property
    def editing(self)->bool:
        return (self.status_.isSet(self.EDIT_MODE_CREATION) or self.status_.isSet(self.EDIT_MODE_RESOLUTION))
    @editing.setter
    def editing(self, active: bool = True):
        if not active:
            self.status_.set(self.EDIT_MODE_CREATION, False)
            self.status_.set(self.EDIT_MODE_RESOLUTION, False)

    # Selection status
    @property
    def selected(self)->bool:
        return self.selected_
    @selected.setter
    def selected(self, set: bool = True):
        self.selected_ = set
    def changeSelectedStatus(self)->bool:
        self.selected_ = not self.selected_
        return self.selected_

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

    # Constructor
    #
    def __init__(self, params : options):
        self.initDone_: bool = False
        self.params_: options = params
        self.params_.center = True

        self.sudoku_: sudoku = sudoku()    # First, the array is empty
        self.stats_: stats = stats()
        self.edition_: editStatus = editStatus()
        self.prevValues_: list[prevValue] = []   # List of prev. values during edition

        # Dimensions
        self.offsets_: tuple[int,int] = (0,0)
        self.width_:int = 0        # Window's dimensions
        self.height_: int = 0
        self.intSquareWidth_:int = 0        # Internal dims of an element
        self.extSquareWidth_:int = 0        # Ext. dims
        self.canvasFontSize_: int = 0
        self.tagWidth_:int = 0

        self.theme_: GUITheme.ownTheme = GUITheme.ownTheme()

    @property
    def initialized(self)->bool:
        return self.initDone_
    @initialized.setter
    def initialized(self, newVal : bool):
        self.initDone_ = newVal

    # GUI initialization
    #
    def initialize(self):
        # Default dimensions
        self.width_ = ROW_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_W
        self.height_ = LINE_COUNT * GUIConsts.SQUARE_SIDE + 2 * GUIConsts.DELTA_H
        self.offsets_ = (GUIConsts.DELTA_W, GUIConsts.DELTA_H)
        self.extSquareWidth_ = GUIConsts.SQUARE_SIDE
        self.intSquareWidth_ = GUIConsts.SQUARE_SIDE - 2 * GUIConsts.EXT_BORDER_THICK

        self._theme_changeByName(GUITheme.DEF_THEME_NAME)
        self._draw_fontSize2PixelSize()

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
    def setFilename(self, fileName:str | None, create:bool = False):
        if fileName is not None:
            # the file must exists
            if False == create and False == os.path.isfile(fileName):
                raise sudokuError(f"solver::setFilename - {fileName} is not a file or does not exist")
            self.filename = fileName

    # Start drawings / UI
    #
    def startUI(self):
        pass

    # End drawings
    #
    def end(self):
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

        self.setFilename(fileName)

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

            position: pointer = pointer(game = False)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    currentElement = elements[position.index()]
                    bk, txt = self._theme_getElementColours(position.index(), False)
                    self._draw_singleElement(
                        row, line,
                        currentElement.num,
                        bk, txt,
                        currentElement.hypothesis,
                    )

                    # next element ...
                    position+=1

            self._draw_end()

    # Update the whole window
    #
    def draw_update(self):
        self.draw(redrawBackground=True)

    def _draw_startUp(self):
        pass

    def _draw_end(self):
        pass

    # Draw selected element (on edit mode)
    #
    def _draw_selectedElement(self, selected : bool = True):
        index:int = self.edition_.currentPos_.index()
        currentElement : element =self.sudoku_[index]
        value : int | None = currentElement.num
        self._draw_startUp()

        bk, txt = self._theme_getElementColours(index, selected)
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
    def _draw_newClientSize(self, newWidth:int, newHeight:int, boxWidth:int | None = None):
        self.width_ = newWidth
        self.height_ = newHeight

        # Compute new square sizes
        squareW = boxWidth if boxWidth is not None else math.floor((newWidth - 2 * GUIConsts.DELTA_W) / ROW_COUNT)
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

        self._draw_fontSize2PixelSize()

        # tag dims.
        self.tagWidth_ = int(GUIConsts.TAG_MIN_SIZE * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE)
        if self.tagWidth_ % 2 != 0:
            self.tagWidth_+=1
        self.tagWidth_ = min(self.tagWidth_, GUIConsts.TAG_MAX_SIZE)

    # Font size in pixels (based on theme's original size)
    def _draw_fontSize2PixelSize(self):
        self.canvasFontSize_ = int(self.theme_.canvasFont_.size * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE)

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

    #
    # Array edition
    #

    # Start edition mode
    #
    def _edit_start(self, initPos:bool = True):
        self.prevValues_.clear()        # Nothing to undo or cancel

    # End of edition mode
    #
    def _edit_stop(self, endApp:bool = False):
        self.edition_.editing = False   # !!!

    # Update array during edition
    #
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        self._draw_startUp()

        if prevPos is not None :
            prevElement : element = self.sudoku_[prevPos.index()]
            bk, txt = self._theme_getElementColours(prevPos.index_, False)

            # if sel. changed, erase previously selected element
            self._draw_singleElement(
                prevPos.row(),
                prevPos.line(),
                self.sudoku_.elements_[prevPos.index()].num,
                bk, txt,
                prevElement.hypothesis
            )

        # Select the new value
        index: int = self.edition_.currentPos_.index()
        currentElement : element = self.sudoku_[index]
        bk, txt = self._theme_getElementColours(index, True)
        self._draw_singleElement(
            currentPos.row(),
            currentPos.line(),
            self.sudoku_[currentPos.index()].num,
            bk, txt,
            currentElement.hypothesis
        )

        self._draw_end()

    # (try to) set a value
    #
    #  @return : Index of modified item or -1 if nothing has been done
    #
    def _edit_setValue(self, val: int)->int:
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_[index].isChangeable():
            return -1

        if self.sudoku_.checkValue(self.edition_.currentPos_, val):
            return self._edit_setValueEx(val, id= index)

        return -1

    def _edit_setValueEx(self, val: int, id:int = -1, keep:bool = True)->int:
        index:int = id if id != -1 else self.edition_.currentPos_.index()
        if keep:
            self.prevValues_.append(prevValue(index, self.sudoku_[index].num))
        #self.sudoku_.elements_[index].setValue(val, element.STATUS_ORIGINAL, True)
        self.sudoku_.modifyAt(pointer(index, False), value=val,
            status=(element.STATUS_ORIGINAL if self.edition_.creating else 0) | element.STATUS_SET)
        self.edition_.status_.set(editStatus.EDIT_NO_REDRAW | editStatus.EDIT_MODIFIED)
        return index

    # Decrease value
    #
    def _edit_decValue(self)->bool:
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_[index].isChangeable():
            return False

        val : int | None = self.sudoku_[index].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findPreviousValue(self.edition_.currentPos_, val)
        if newVal != val:
            return (-1 != self._edit_setValueEx(newVal, index))
        return False

    # Inc value
    #
    def _edit_incValue(self)->bool:
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_[index].isChangeable():
            return False
        val : int | None = self.sudoku_[index].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findNextValue(self.edition_.currentPos_, val)
        if newVal != val:
            return (self._edit_setValueEx(newVal, index) != -1)

        return False

    # Remove current value
    #
    def _edit_removeValue(self)->bool:
        index:int = self.edition_.currentPos_.index()
        if self.edition_.manualSolving and not self.sudoku_[index].isChangeable():
            return False

        self.sudoku_.clearAt(self.edition_.currentPos_.index(), True)
        return True

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
                self.sudoku_[val.index_].setValue(val.value_, element.STATUS_ORIGINAL, True)
            else:
                self.sudoku_[val.index_].empty(True)

        self.prevValues_.clear()
        return True

    # Mouse position : client -> array coordinates
    #
    # @return : (ZoneID, x coordinate, y coordinate)
    #           If ZoneID == ZONE_NOWHERE, x and y are undefined
    #
    def _mouse_translatePosition(self, pos: tuple[int,int])->tuple[int, int, int]:
        ret:list[int] = [-1,-1]
        if len(self.sudoku_) == ARRAY_SIZE:
            for index in range(2):
                if pos[index] > self.offsets_[index]:
                    ret[index] = int((pos[index] - GUIConsts.EXT_BORDER_THICK - self.offsets_[index]) / self.extSquareWidth_)
                else:
                    return (ownZone.ZONE_NOWHERE, 0, 0)
        return (ownZone.ZONE_ARRAY, ret[0], ret[1]) if ret[0]<ROW_COUNT and ret[1]<LINE_COUNT else (ownZone.ZONE_NOWHERE, 0, 0)

    #
    #  Element(s)' notifications
    #

    def _notify_start(self, freq:int = GUIConsts.TIMER_RATE_SELECTED, max:int = GUIConsts.BLINK_COUNT_MODIFYING):
        pass

    def _notify_drawElements(self):
        pass

    def _notify_stop(self, endApp:bool = False):
        self.sudoku_.notify_end() # remove elements statusbit

    #
    # Resolution
    #

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
    def _resolve_showStats(self):
        print(f"\n\t- {self.filename}")

        # Found obvious values ?
        if self.params_.obviousValues:
            if self.stats_.obvValues_:
                print("\t- Found " + str(self.stats_.obvValues_) + " obvious value(s) in " + str(round(self.stats_.obvDuration_, 2)) + " second(s)")
            else:
                print("\t- No obvious value found")

        print("\t- Solved in " + str(round(self.stats_.bruteDuration_, 2)) + " second(s)")
        print("\t- " + str(self.stats_.bruteAttempts_) + " attempt(s)\n")


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

    #
    # Themes
    #

    # Get elements text and bk colours for edition or creation
    #
    #  @pos : Element's position
    #  @sekected : Element is selected ?
    #
    #  @return : Tuple(bk Colour, txt Colour)
    def _theme_getElementColours(self, pos: int, selected:bool = False)->tuple[int,int]:
        position:pointer = pointer(pos)
        bkColour:int = GUITheme.colourID.ID_SEL_BK if selected else GUITheme.colourID.ID_FRAME_BK_ODD if position.squareID() % 2 else GUITheme.colourID.ID_FRAME_BK_EVEN

        #if self.edition_.creating and not self.sudoku_.elements_[pos].notifying:
        if self.edition_.creating:
            return bkColour, GUITheme.colourID.ID_ORIGINAL_TXT   # always use "original" colour

        if self.sudoku_[pos].isObvious():
            return bkColour, GUITheme.colourID.ID_OBVIOUS_TXT
        else:
            if self.sudoku_[pos].isOriginal():
                return bkColour, GUITheme.colourID.ID_ORIGINAL_TXT

        return bkColour, GUITheme.colourID.ID_SEL_TXT if selected else GUITheme.colourID.ID_DEFAULT_TXT

    # Convert colour objects from ownColour to specific (to GUI tools)  colour format
    #
    def _theme_convertColours(self):
        pass

    # Change current GUI theme
    #
    def _theme_changeByName(self, name:str)->bool:
        if name not in list(GUITheme.colourThemes.keys()):
            print(f"Error - '{name}' is not a valid theme name. The theme '{GUITheme.DEF_THEME_NAME}' will be use instead")
            name = GUITheme.DEF_THEME_NAME

        if len(GUITheme.colourThemes[name]["colours"]) != GUITheme.colourID.ID_COLOUR_COUNT:
            print(f"Error - The colour-list for the theme '{name}' is incomplete. The theme '{GUITheme.DEF_THEME_NAME}' will be use instead")
            name = GUITheme.DEF_THEME_NAME

        if name == self.theme_.name:
            return False    # Theme has not changed

        # Retreive fonts informations
        self.theme_.name = name

        try:
            self.theme_.canvasFont_.faceName = GUITheme.colourThemes[name]["fonts"]["canvas"]["faceName"]  # pyright: ignore[reportCallIssue, reportArgumentType, reportAttributeAccessIssue]
            self.theme_.canvasFont_.size = GUITheme.colourThemes[name]["fonts"]["canvas"]["size"]  # pyright: ignore[reportCallIssue, reportArgumentType, reportAttributeAccessIssue]
            self.theme_.canvasFont_.weight = self._theme_getFontWeight(name, "canvas")
            self.theme_.canvasFont_.italic = self._theme_isItalic(name, "canvas")

            self.theme_.textFont_.faceName = GUITheme.colourThemes[name]["fonts"]["messages"]["faceName"]  # pyright: ignore[reportCallIssue, reportArgumentType, reportAttributeAccessIssue]
            self.theme_.textFont_.size = GUITheme.colourThemes[name]["fonts"]["messages"]["size"]  # pyright: ignore[reportCallIssue, reportArgumentType, reportAttributeAccessIssue]
            self.theme_.textFont_.weight = self._theme_getFontWeight(name, "messages")
            self.theme_.textFont_.italic = self._theme_isItalic(name, "messages")

            # Transfer colours in internal list for conversion
            self.theme_.clear() # clear the colours list
            for col in GUITheme.colourThemes[name]["colours"] :
                if isinstance(col, tuple) and len(col) == 3:
                        self.theme_.append(GUITheme.ownColour(col)) # col is a tuple !!!

            self._theme_convertColours() # Convert colours
            return True

        except KeyError:
            print(f"Error - The theme '{name}' is incomplete or invalid.")
        except IndexError:
            print(f"Error - The theme '{name}' doesn't contain enough clours.")

        return False

    # Get font's weight from theme
    #
    def _theme_getFontWeight(self, themeName:str, fontName:str)->GUITheme.ownWeight:
        weight:GUITheme.ownWeight = GUITheme.ownWeight.NORMAL

        if "weight" in GUITheme.colourThemes[themeName]["fonts"][fontName]:  # pyright: ignore[reportArgumentType, reportCallIssue]
            style:str = GUITheme.colourThemes[themeName]["fonts"][fontName]["weight"]  # pyright: ignore[reportArgumentType, reportCallIssue, reportAssignmentType, reportUnknownVariableType]

            match style:
                case "extra thin":
                    weight = GUITheme.ownWeight.EXTRA_THIN
                case "thin":
                    weight = GUITheme.ownWeight.THIN
                case "light":
                    weight = GUITheme.ownWeight.LIGHT
                case "medium":
                    weight=GUITheme.ownWeight.MEDIUM
                case "bold":
                    weight=GUITheme.ownWeight.BOLD
                case "extra bold":
                    weight = GUITheme.ownWeight.EXTRA_BOLD

                case "normal" | _:
                    pass

        return weight

    # Is font italic ?
    #
    def _theme_isItalic(self, themeName:str, fontName:str)->bool:
        italic=False

        if "italic" in GUITheme.colourThemes[themeName]["fonts"][fontName]:  # pyright: ignore[reportArgumentType, reportCallIssue]
            response:str = GUITheme.colourThemes[themeName]["fonts"][fontName]["italic"]  # pyright: ignore[reportArgumentType, reportAssignmentType, reportCallIssue, reportUnusedVariable, reportUnknownVariableType]
            italic = response in ('True', 'true', 'yes')

        return italic

# EOF
