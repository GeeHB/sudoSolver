# coding=UTF-8
#
#   File        :   cursesOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   cursesOutputs object definition
#                   Display a Sudoku grid using (n)Curses library (Unix / Linux and MacOS)
#

from ownExceptions import sudokuError
from outputs import outputs
from pointer import pointer

import curses

# 
# Internal consts
#

COLOUR_EVEN_ID  = 1
COLOUR_ODD_ID   = 2

ORIGIN_X = 5
ORIGIN_Y = 5

#
# cursesOutputs - Display a Sudoku grid using (n)Curses 
#
class cursesOutputs(outputs):

    term_ = None      # curses "window"

    # Construction
    #
    def __init__(self, showDetails = False):
        self.term_ = curses.initscr()
        curses.cbreak()
        self.term_.keypad(True)
        self.term_.nodelay(True)
        curses.curs_set(0)

        # colors ?
        if False == curses.has_colors():
            raise sudokuError("Curses must accept colors")

        curses.start_color()
        curses.init_pair(COLOUR_EVEN_ID, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(COLOUR_ODD_ID, curses.COLOR_BLUE, curses.COLOR_WHITE)

    # Display text
    #
    def displayText(self, text, information, elements):
        # no text with curses. Except when curses is not launched ...
        if None == self.term_:
           super().displayText(text) 
    
    # Draw the whole matrix
    #
    def draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):
                
                currentElement = elements[position.index()]

                attr = curses.color_pair(COLOUR_EVEN_ID) if 0 == (position.squareID() % 2) else curses.color_pair(COLOUR_ODD_ID)
                if currentElement.isOriginal():
                    attr |= curses.A_BOLD # "original" elements are bold

                self.term_.addstr(ORIGIN_Y + line, ORIGIN_X + 3 * row, " " + (" " if currentElement.isEmpty() else str(currentElement.value())) +  " ", attr) 
                
                # next element ...
                position+=1
        
        # don't forget to refresh the console !
        self.term_.refresh()
    
    # Finish ...
    #
    def close(self):
        if self.term_:
            # close curses
            curses.endwin()
            self.term_ = None

 # EOF