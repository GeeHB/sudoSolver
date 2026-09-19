# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver and ownColour objects
#                       - GUI for sudoku solver
#
import time
from enum import IntEnum, auto
from typing import Any

import ownExceptions
from element import element
from options import (
    BK_COLOUR,
    BK_COLOUR_FILENAME,
    BORDER_COLOUR,
    HILITE_COLOUR,
    SEL_BK_COLOUR,
    SEL_TXT_COLOUR,
    TXT_COLOUR,
    options,
    stats,
)
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
    pointer,
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

    @property
    def initialized(self)->bool:
        return self.initDone_
    @initialized.setter
    def initialized(self, newVal : bool):
        self.initDone_ = newVal

    @property
    def multithreaded(self)->bool:
        return self.params_.progressMode_ == options.PROGRESS_MULTITHREADED

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
        pass

    # Start drawings / UI
    #
    def start(self):
        pass

    # Draw the whole array
    #
    #   elements :  array of elements to draw or None.
    #               if None, current sudoku will be drawn
    #
    def draw(self, elements : list[element] | None = None, redrawBackground : bool = False):
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
        if self.multithreaded:
            found = self._resolveMultiThreaded()
        else:
            try:
                self.sudoku_.resolveSingleThreaded()
            except ownExceptions.reachedEndOfList:
                # Found a solution !!!
                found = True
            except IndexError:
                # No solution found
                self.sudoku_.attempts = 0

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

    # Multi-threaded mode
    #
    # returns True if a solution has been founded
    def _resolveMultiThreaded(self)->bool:
        self.sudoku_.resolveMultiThreaded() # start resolution thread
        while self.sudoku_.is_alive():
            self.draw(redrawBackground=False)     # redraw sudoku while searching for a solution

        return self.sudoku_.found
# EOF
