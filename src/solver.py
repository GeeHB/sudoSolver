# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver object
#                       - abstract class
#

from options import options, stats
from sArray import sArray


class solver:
    def __init__(self, params : options):
        self.initDone_ = False
        self.params_ : options = params
        self.sudoku_ : sArray = sArray()    # First empty array
        self.stats_ : stats = stats()

    @property
    def initialized(self)->bool:
        return self.initDone_
    @initialized.setter
    def initialized(self, newVal : bool):
        self.initDone_ = newVal

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

    # Show resolution stats
    #
    #   Print stats on console (by default)
    #
    def showStats(self):
        print("\t- " + self.params_.fileName_)

        # Found obvious values ?
        if self.params_.obviousValues:
            if self.stats_.obvValues_:
                print("\t- Found " + str(self.stats_.obvValues_) + " obvious value(s) in " + str(round(self.stats_.obvDuration_, 2)) + " second(s)")
            else:
                print("\t- No obvious value found")

        print("\t- Solved in " + str(round(self.stats_.bruteDuration_, 2)) + " second(s)")
        print("\t- " + str(self.stats_.bruteAttempts_) + " attempt(s)\n")

# EOF
