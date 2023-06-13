# coding=UTF-8
#
#   File        :   outputs.py
#
#   Author      :   GeeHB
#
#   Description :   outputs object
#                   Abstract class, base for all drawings
#

import os
from ownExceptions import sudokuError


#
# stats - Informations about a solution
#
class stats(object):
    obvValues_ = 0          # Count of obvious values found
    obvDuration_ = 0        # Duration in sec. of obvious-values search process

    bruteDuration_ = 0      # Duration in sec. of brute-force search process
    bruteAttempts_  = 0     # Brute-force attempts counter


#
# outputs - abstract class containing all drawing methods 
#
class outputs(object):

    #
    # Public consts
    #

    EVT_KEYDOWN         = None  # By default the event doesn't exist
    EVT_QUIT            = None

    EVT_MOUSEBUTTONDOWN = None  # No mouse

    # Mouse button ID
    MOUSE_BUTTON_NONE   = None
    MOUSE_BUTTON_LEFT   = 1
    MOUSE_BUTTON_MIDDLE = 2
    MOUSE_BUTTON_RIGHT  = 4

    # Defined keys
    #
    MOVE_LEFT           = "s"     # Moving in the grid (or in browse mode)
    MOVE_RIGHT          = "f"
    MOVE_UP             = "e"
    MOVE_DOWN           = "x"
    
    REMOVE_VALUE        = " "

    VALUE_DEC_OLD       = "+"     # Change element value (edition mode)
    VALUE_INC_OLD       = "-"

    VALUE_DEC           = "q"     # Change element value (edition mode)
    VALUE_INC           = "w"

    VALUE_1             = "1"     # Set value (edition mode)
    VALUE_9             = "9"

    EDIT_CANCEL         = "q"
    EDIT_QUIT_AND_SAVE  = "w"

    #  App colours
    #
    BORDER_COLOUR       = (81, 154, 186)
    BK_COLOUR           = (230, 230, 255)
    BK_COLOUR_FILENAME  = (220, 220, 245)
    TXT_COLOUR          = (64, 64, 64)
    HILITE_COLOUR       = (248, 128, 112)
    OBVIOUS_COLOUR      = BORDER_COLOUR

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

    mode_ = MODE_DEFAULT       # Display mode
    gridFileName_ = None

    keyHandler_ = None


    # Ready to go ?
    #
    # can be overloaded
    def isReady(self):
        return True

    # Use GUI ?
    #
    # can be overloaded
    def useGUI(self):
        return False

    # Display text
    #
    # can be overloaded
    def displayText(self, text, information = True, elements = None):
        # By default, text is displayed on the console
        print(text)

    # Show resolution stats
    #   
    #   Print stats on console (by default)
    #
    # can be overloaded
    def showStats(self, params, sStats):
        print("\t- " + params.fileName_)

        # Found obvious values ?
        if True == params.obviousValues_:
            if sStats.obvValues_:
                print("\t- Found " + str(sStats.obvValues_) + " obvious value(s) in " + str(round(sStats.obvDuration_, 2)) + " second(s)")
            else:
                print("\t- No obvious value found")

        print("\t- Solved in " + str(round(sStats.bruteDuration_, 2)) + " second(s)")
        print("\t- " + str(sStats.bruteAttempts_) + " attempt(s)\n") 

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

    # Check current/last event
    #
    def pollEvent(self):
        return self.waitForEvent()
    
    # Mouse events and status
    #
    #   returns tuple (ButtonID or None, (xPos, yPos))
    #
    def mouseButtonStatus(self, event):
        return self.MOUSE_BUTTON_NONE, (0, 0)
    
    # Mouse position
    #
    def mousePosition(self, pos):
        return None

    # Is a key pressed ?
    #
    #   returns the tuple (pressed?, key or None if not pressed)
    #
    #  can be overloaded
    def keyPressed(self, elements = None, allEvents = False):
        return (False, None)    

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

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements):
        pass

    # Solving process eneded
    #   can be overloaded
    def endedSolving(self):
        pass

    # Update display from beginning to 'limit' (if not None)
    #
    def updateGrid(self, elements, limit):
        self._updateGrid(elements, limit)
        
    # End of the object (no more drawings at all)
    #   can be overloaded
    def close(self):
        pass

    #
    # "private" methods
    #

    # Update display from beginning to 'limit' (if not None)
    # can be overloaded
    def _updateGrid(self, elements, limit):
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