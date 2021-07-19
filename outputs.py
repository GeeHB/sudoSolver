# coding=UTF-8
#
#   File     :   outputs.py
#
#   Author      :   JHB
#
#   Description :   outputs object
#                   Abstract class, base for all drawings
#
#   Version     :   1.1.2
#
#   Date        :   2021-07-19
#

import os, sys, time, os
from ownExceptions import sudokuError
from pointer import pointer

#
# outputs - abstract class containing all drawing methods 
#
class outputs(object):

    #
    # Public consts
    #

    EVT_KEYDOWN         = None  # By default the event doesn't exist
    EVT_QUIT            = None

    # Defined keys
    #
    MOVE_LEFT           = "s"     # Moving in the grid (or in browse mode)
    MOVE_RIGHT          = "f"
    MOVE_UP             = "e"
    MOVE_DOWN           = "x"
    
    VALUE_DEC           = "+"     # Change element value (edition mode)
    VALUE_INC           = "-"

    EDIT_CANCEL         = "q"
    EDIT_QUIT_AND_SAVE  = "w"

    #  App colours
    #
    BORDER_COLOUR       = (81, 154, 186)
    BK_COLOUR           = (230, 230, 255)
    BK_COLOUR_FILENAME  = (220, 220, 245)
    TXT_COLOUR          = (64, 64, 64)
    HILITE_COLOUR       = (248, 128, 112)

    SEL_BK_COLOUR       = (50, 50, 255)
    SEL_TXT_COLOUR      = (255, 255, 255)

    # Display modes
    #
    MODE_DEFAULT        = 0 
    MODE_EDIT           = 1
    MODE_BROWSEFOLDER   = 2

    #
    # "private" members
    #

    # Display grid during resolution
    detailsRatio_ = 0          # Display rate (0 = none)
    detailsCount_ = 0

    mode_ = MODE_DEFAULT       # Display mode
    gridFileName_ = None

    keyHandler_ = None

    def setDetailsRatio(self, detailsRatio = 0):
        self.detailsRatio_ = detailsRatio

    # Display text
    #
    # can be overloaded
    def displayText(self, text, information = True, elements = None):
        # By default, text is displayed on the console
        print(text)

    # Waiting for an event
    #   @allEvents : returns when any event occurs (by default only keyboard and exit events)
    #   returns the event
    #
    #  can be overloaded
    def waitForEvent(self, elements = None, allEvents = False):
        wait = True
        while wait:
            c = self._readKeyboard()
            wait = (len(c) == 0)    

    # Is this display mode compatible with edition ?
    def allowEdition(self):
        return not (0 == (self.mode_ & self.MODE_EDIT))

    # Is this display mode compatible with forlder browsing ?
    def allowFolderBrowsing(self):
        return not (0 == (self.mode_ & self.MODE_BROWSEFOLDER))

    # Set/change the current grid's filename
    #   can be overloaded
    def setGridName(self, fileName):
        # the file must exists
        if False == os.path.isfile(fileName):
            raise sudokuError(fileName +  " is not a file")
        self.gridFileName_ = fileName

    # Draw all the grid
    #   can be overloaded
    def draw(self, elements):
       pass

    # Draw a single element in the grid
    #   can be overloaded
    def drawSingleElement(self, row, line, value, bold, bkColour, txtColour):
        pass

    # Update the window
    #   can be overloaded
    def update(self):
        pass

    # Update display from beginning to 'limit' (if not None)
    #
    def updateGrid(self, elements, limit):
        
        if self.detailsRatio_ > 0 :
            # Display details ?
            self.detailsCount_ += 1
            if 0 == (self.detailsCount_ % self.detailsRatio_):
                self._update(elements, limit)
                self.detailsCount_ = 0

    # End of the object (no more drawings at all)
    #   can be overloaded
    def close(self):
        pass

    #
    # "private" methods
    #

    # Update display from beginning to 'limit' (if not None)
    # can be overloaded
    def _update(self, elements, limit):
      pass  

    # Read the keyboard
    # returns  a  char
    def _readKeyboard(self):
        # Loaded ?
        if None == self.keyHandler_:
            try:
                import posixKeyboard
                self.keyHandler_ = posixKeyboard.posixKeyboard()
            except ModuleNotFoundError:
                import msKeyboard
                self.keyHandler_ = msKeyboard.msKeyboard()

        # handle the key
        return self.keyHandler_.getChar()
        


        
 # EOF