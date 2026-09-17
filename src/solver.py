# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver object
#                       - abstract class
#
import time

import ownExceptions
from element import element
from options import options, stats
from sudoku import sudoku


class solver:
    def __init__(self, params : options):
        self.initDone_ : bool = False
        self.params_ : options = params
        self.sudoku_ : sudoku = sudoku()    # First, the array is empty
        self.stats_ : stats = stats()

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

    # Draw the full array
    #
    def draw(self, elements : list[element] | None = None, redrawBackground : bool = False):
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
        try:
            if self.multithreaded:
                found = self._resolveMultiThreaded()
            else:
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
    def _resolveMultiThreaded(self)->bool:
        self.sudoku_.resolveMultiThreaded() # start resolution thread
        while self.sudoku_.is_alive():
            self.draw()     # redraw sudoku while searching solution

        return self.sudoku_.found
# EOF
