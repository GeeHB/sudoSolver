#!/usr/bin/env python
#
# coding=UTF-8
#
#   File        :   pygameOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of pygameOutputs and textSurfcace objects
#                   Displays the grid using PYGame
#

import math
import os
import sys

try :
    import pygame
except ModuleNotFoundError:
    print("pygame not installed - pip install pygame | sudo apt/dnf install python(3)-pygame")
    sys.exit(0)
from options import APP_SHORT_NAME
from ownExceptions import sudokuError
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
    pointer,
)
from sharedTools import (
    statusBits,
    systemInfos,
)

#
#
# Internal constants
#

# Positions and dimensions in pixels
#
SQUARE_SIDE_BASE        = 60
SQUARE_SIDE             = 60   # Initial external size of a square element

STATS_FRAME_WIDTH       = 0    # Width in pixels of stats'frame

SQUARE_MIN              = 10   # Minimal square size

DELTA_W                 = 10   # Grid offsets
DELTA_H                 = 10

EXT_BORDER_THICK        = 3    # Thickness of external border

MENUBAR_HEIGHT          = 32

# Elements'text font sizes (in pixels) and names
#
ELT_FONT_NAME           = 'Herculanum,Papyrus,Helvetica'    # The first font in the list ...
ELT_FONT_SIZE           = 35                                # default size

FILE_FONT_NAME          = 'Helvetica,Arial'                 # Grid's name display
FILE_FONT_SIZE          = 25
FILE_FONT_POS_X         = 35
FILE_FONT_POS_Y         = 5

# Events frequencies in ms
#
DEF_MSG_HIDING_FREQ     = 2000  # Hide the filename
DEF_BLINKING_FREQ       = 750   # blinking freq. in ms

#
# stats - Informations about a solution
#
class stats:
    obvValues_ = 0          # Count of obvious values found
    obvDuration_ = 0.0      # Duration in sec. of obvious-values search process

    bruteDuration_ = 0.0    # Duration in sec. of brute-force search process
    bruteAttempts_  = 0     # Brute-force attempts counter

#
# textSurface - "subsurface" containig a single line of text
#
class textSurface:

    # Construction
    def __init__(self, fontName, fontSize):
        # Members
        self.surface_    = None
        self.position_   = (0,0)
        self.font_       = None      # Font used for drawing the text
        self.eventID_    = 0         # Event ID - optionnal
        self.eventFreq_  = 0
        self.setFont(fontName, fontSize)

    # Valid ?
    def isValid(self):
        return bool(self.surface_)

    # Visible ?
    def isVisible(self):
        return self.isValid()

    # My surface
    def surface(self):
        return self.surface_

    # Create / change the font
    def setFont(self, fontName, fontSize):
        if self.font_:
            del self.font_
        self.font_ = pygame.font.SysFont(fontName, fontSize)

    # Create a surface with the associated text
    def setText(self, text, txtColour, bkColour = None):
        self.erase()

        if self.font_ is not None:
            self.surface_ = self.font_.render(text, 1, txtColour, bkColour)

    # Erases the surface
    def erase(self):
        if self.surface_ :
            del self.surface_
            self.surface_ = None

    # End ...
    def end(self):
        self.killTimer()
        self.erase()
        del self.font_

    # Position
    #

    # Bounding rectangle
    def rect(self):
        if self.surface_ is not None :
            return (self.position_[0], self.position_[1], self.surface_.get_width(), self.surface_.get_height())
        return (0,0,0,0)

    # Current position
    def position(self):
        return self.position_

    # Change position
    def moveTo(self, x, y):
        self.position_ = (x,y)

    # Dimensions
    #
    def getWidth(self):
        if self.surface_ is not None :
            return 0 if not self.isVisible() else self.surface_.get_width()
        return 0
    def getHeight(self):
        if self.surface_ is not None :
            return 0 if not self.isVisible() else self.surface_.get_height()
        return 0

    # Event ID
    #
    def eventID(self):
        return self.eventID_
    def setEventID(self, id, freq):
        self.eventID_ = id
        self.eventFreq_ = freq

    # Timer
    #
    def startTimer(self):
        pygame.time.set_timer(self.eventID(), self.eventFreq_)
    def killTimer(self):
        pygame.time.set_timer(self.eventID(), 0)
    def frequency(self):
        return self.eventFreq_

#
# blinkingText - "subsurface" containig a single line of blinking text
#
class blinkingText(textSurface):
    visible_        = True

    # Construction
    def __init__(self, fontName, fontSize):
        super().__init__(fontName, fontSize)

    # Text visibility
    #
    def isVisible(self):
        return self.visible_ if self.isValid() else False
    def setVisible(self, visible = True):
        self.visible_ = visible
    def changeVisibility(self):
        self.visible_ = not self.visible_
        return self.visible_

#
# pygameOutputs - Display sudoku's grid using PYGame library
#
class pygameOutputs:

    EVT_KEYDOWN         = pygame.KEYDOWN
    EVT_QUIT            = pygame.QUIT

    # PYGame keys
    #
    MOVE_LEFT           = pygame.K_LEFT
    MOVE_RIGHT          = pygame.K_RIGHT
    MOVE_UP             = pygame.K_UP
    MOVE_DOWN           = pygame.K_DOWN

    # Mouse click
    EVT_MOUSEBUTTONDOWN = pygame.MOUSEBUTTONDOWN

    # Mouse button ID
    MOUSE_BUTTON_NONE   = 0
    MOUSE_BUTTON_LEFT   = 1
    MOUSE_BUTTON_MIDDLE = 2 # ???
    MOUSE_BUTTON_RIGHT  = 3

    # Change element value
    REMOVE_VALUE        = pygame.K_DELETE
    REMOVE_VALUE_BIS    = pygame.K_BACKSPACE

    VALUE_DEC           = pygame.K_PAGEDOWN
    VALUE_INC           = pygame.K_PAGEUP

    # Set value
    VALUE_1             = pygame.K_1
    VALUE_9             = pygame.K_9

    VALUE_KPAD_1         = pygame.K_KP1  # from keypad
    VALUE_KPAD_9         = pygame.K_KP9

    EDIT_CANCEL         = pygame.K_ESCAPE
    EDIT_QUIT_AND_SAVE  = pygame.K_RETURN

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
    MODE_DEFAULT        = statusBits.STATUS_NONE
    MODE_EDIT           = 1
    MODE_BROWSEFOLDER   = 2

    # Members
    #
    win_            = None     # My window

    width_          = 0        # Window's dimensions
    height_         = 0

    intSquareWidth_ = 0        # Internal dims of an element
    extSquareWidth_ = 0        # Ext. dims

    # Elements'values drawing
    sElement_ = None

    mode_ = statusBits.statusBits()       # Display mode
    gridFileName_ = None

    keyHandler_ = None

    # Display the grid name
    sFileName_       = None

    # Text message
    sMessage_ = None

    # Construction
    #
    def __init__(self, position = None):
        self._start(position)
        self._drawBackground()

    def _start(self, position = None) :
        self.initDone_ = False
        self.mode_.assign(self.MODE_EDIT + self.MODE_BROWSEFOLDER)

        # Init. the lib.
        rets = pygame.init()

        if 0 != rets[1] :
            raise sudokuError(f"PYGame initialization error - PYGame returns {rets[1]!r} error(s)")

        # PYGame init. is ok
        self.initDone_ = True

        # Default dimensions
        self.width_ = ROW_COUNT * SQUARE_SIDE + 2 * DELTA_W + STATS_FRAME_WIDTH
        self.height_ = MENUBAR_HEIGHT + LINE_COUNT * SQUARE_SIDE + 2 * DELTA_H
        self.extSquareWidth_ = SQUARE_SIDE
        self.intSquareWidth_ = SQUARE_SIDE - 2 * EXT_BORDER_THICK

        # font for drawing elements
        fontSize = int(ELT_FONT_SIZE * self.intSquareWidth_ / SQUARE_SIDE_BASE)
        self.sElement_ = textSurface(ELT_FONT_NAME, fontSize)
        self.sElement_.moveTo((self.extSquareWidth_ - fontSize) / 2, 0)

        # Main window creation
        myDict = systemInfos.getSystemInformations()
        #myDict = None
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.SCALED if myDict is not None and myDict[systemInfos.KEY_WM] == systemInfos.WM_CHROMEOS else pygame.RESIZABLE )

        pygame.display.set_caption(APP_SHORT_NAME)

        # Place the Window
        systemInfos.setMainWindowPosition(position)

        # fileName displays
        self.sFileName_ = textSurface(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.sFileName_.moveTo(FILE_FONT_POS_X, FILE_FONT_POS_Y)
        self.sFileName_.setEventID(pygame.USEREVENT + 1, DEF_MSG_HIDING_FREQ)   # event for text hiding

        # Messages
        self.sMessage_ = blinkingText(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.sMessage_.setEventID(pygame.USEREVENT + 2, DEF_BLINKING_FREQ)

    # Ready to go ?
    #
    # can be overloaded
    def isReady(self) -> bool:
        return True

     # Is this display mode compatible with edition ?
    def allowEdition(self):
        return self.mode_.isSet(self.MODE_EDIT)

    # Is this display mode compatible with forlder browsing ?
    def allowFolderBrowsing(self):
        return self.mode_ .isSet(self.MODE_BROWSEFOLDER)

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

    # Display text
    #
    def displayText(self, text, information, elements):
        if True == information:
            # By default, text is displayed on the console
            print(text)
        else:
            self._int_displayText(text, elements)

    def _int_displayText(self, text, elements):
        # Display text on top of the board
        self._showMessage(text, elements)
        self._int_refresh(elements)

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements):
        pass

    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents) -> pygame.event.Event:
        return self._int_waitForEvent(elements, allEvents)

    def _int_waitForEvent(self, elements, allEvents)  -> pygame.event.Event:
        event = pygame.event.Event(0)
        if self.win_ is not None:
            finished = False
            while not finished:
                event = pygame.event.wait()
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN :
                    finished = True
                elif event.type == pygame.VIDEORESIZE:

                    # Update surface size
                    self._onResizeWindow(self.win_.get_width(), self.win_.get_height())

                    # Resize the surface
                    #self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)
                    #print(f"W : {self.width_} x H : {self.height_}")

                    # Draw bkgrnd & lines ...
                    self._int_drawBackground()

                    # ... and the grid's content
                    if not elements is None:
                        self._int_draw(elements)

                    # returns all events ?
                    if True == allEvents:
                        finished = True

                        #pass
                # New filename to display
                elif self.sFileName_ is not None and event.type == self.sFileName_.eventID():
                    # Erase the name
                    self.sFileName_.erase()
                    self._int_refresh(elements)

                    # kill the timer
                    self.sFileName_.killTimer()
                    if True == allEvents:
                        finished = True
                # Blinking text
                elif self.sMessage_ is not None and event.type == self.sMessage_.eventID():
                    # Change text visibility
                    self.sMessage_.changeVisibility()
                    self._refresh(elements)
                    if True == allEvents:
                        finished = True
        return event

    # Check current/last event
    #
    def pollEvent(self) -> pygame.event.Event:
        return self._int_pollEvent()

    def _int_pollEvent(self) -> pygame.event.Event:
        event = pygame.event.poll()

        # Keyboard translations
        if event.type == pygame.KEYDOWN:
            # turn keypad num keys into num keys
            if  event.key >= self.VALUE_KPAD_1 and event.key <= self.VALUE_KPAD_9:
                event.key = self.VALUE_1 + event.key - self.VALUE_KPAD_1
            # DEL == Backspace
            else :
                if event.key == self.REMOVE_VALUE_BIS:
                    event.key = self.REMOVE_VALUE

        return event

    # All events ...
    #
    def getEvents(self):
        return pygame.event.get()

    # Mouse events and status
    #
    #   returns tuple (ButtonID or None, (xPos, yPos))
    #
    def mouseButtonStatus(self, event):
        return (self.MOUSE_BUTTON_NONE, (0,0)) if event is None else (event.button, event.pos)

    # Is a key pressed ?
    #
    #   returns the list [pressed?, key or None if not pressed]
    #
    def keyPressed(self, elements = None, allEvents = False):
        return self._int_keyPressed(elements, allEvents)

    def _int_keyPressed(self, elements = None, allEvents = False):
        evt = pygame.event.poll()
        valid = (evt.type == pygame.QUIT or evt.type == pygame.KEYDOWN)
        return [True, evt] if valid else [False, None]

    # Set/change the current grid's filename
    #
    def setGridName(self, fileName, create = False):
        self._int_setGridName(fileName, create)

    def _int_setGridName(self, fileName, create = False):
        # the file must exists
        if False == create and False == os.path.isfile(fileName):
            raise sudokuError(fileName +  " is not a file")
        self.gridFileName_ = fileName

        if self.sFileName_ is not None :
            self.sFileName_.setText(fileName, self.TXT_COLOUR, self.BK_COLOUR_FILENAME)

            # erase this name after a while ...
            self.sFileName_.startTimer()

    # Mouse position
    #
    def mousePosition(self, pos):
        return (-1 if pos[0] < DELTA_W else int((pos[0] - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_), -1 if pos[1] < (MENUBAR_HEIGHT + DELTA_H) else int((pos[1] - MENUBAR_HEIGHT - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_))

    # Draw the whole grid
    #
    def draw(self, elements):
        self._int_draw(elements)

    def _int_draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(LINE_COUNT):
            for row in range(ROW_COUNT):
                currentElement = elements[position.index()]
                self._int_drawSingleElement(row, line, currentElement.value(), self.BK_COLOUR, self.HILITE_COLOUR if currentElement.isOriginal() else self.OBVIOUS_COLOUR if currentElement.isObvious() else self.TXT_COLOUR)

                # next element ...
                position+=1

        self._int_update()

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row, line, value, bkColour, txtColour):
        self._int_drawSingleElement(row, line, value, bkColour, txtColour)

    def _int_drawSingleElement(self, row, line, value, bkColour, txtColour):

        # too small to be drawn ?
        if self.win_ is None or 0 == self.extSquareWidth_ :
            return

        # top-left corner position
        x = DELTA_W + row * self.extSquareWidth_ + EXT_BORDER_THICK
        y = MENUBAR_HEIGHT + DELTA_H + line * self.extSquareWidth_ + EXT_BORDER_THICK

        # Erase background
        pygame.draw.rect(self.win_, bkColour, (x, y, self.intSquareWidth_, self.intSquareWidth_))

        # The value (if valid)
        if value is not None and self.sElement_ is not None:
            self.sElement_.setText(str(value), txtColour)

            # Center the text
            mySurface = self.sElement_.surface()
            if mySurface is not None:
                dx = (self.intSquareWidth_ - self.sElement_.getWidth()) / 2
                dy = (self.intSquareWidth_ - self.sElement_.getHeight()) / 2
                self.win_.blit(mySurface, (x + dx, y + dy))

    # Update the window
    #
    def update(self):
        self._int_update()

    def _int_update(self):
        if self.win_ is not None:
                # Display filename ?
            if self.sFileName_ is not None and self.sFileName_.isValid():
                # draw the name
                mySurface = self.sFileName_.surface()
                if mySurface is not None:
                    self.win_.blit( mySurface, self.sFileName_.position())

            # A message ?
            if self.sMessage_ and self.sMessage_.isVisible():
                x = int((self.width_ - self.sMessage_.getWidth())/2)
                y = int((self.height_ - self.sMessage_.getHeight())/2)

                # draw the text
                mySurface = self.sMessage_.surface()
                if mySurface is not None:
                    self.win_.blit(mySurface, (x,y))

            pygame.display.update()

    def flip(self):
        pygame.display.flip()

    # Position of the Window
    def getWindowPosition(self):
        return systemInfos.getMainWindowPosition()
    # Close the display
    def close(self):
        if self.initDone_ and self.sFileName_ is not None and self.sMessage_ is not None:
            # Close text objects
            self.sFileName_.end()
            self.sMessage_.end()

            # close the display
            pygame.display.quit()
            pygame.quit()

    # "private" methods
    #

    # Refresh the whole window
    #
    # can be overloaded
    #
    def _refresh(self, elements):
        self._int_refresh(elements)

    def _int_refresh(self, elements):
        self._int_drawBackground()
        if elements:
            self._int_draw(elements)
        else:
            self._int_update()

    # Handle window's resize
    #
    def _onResizeWindow(self, newWidth, newHeight):

        self.width_ = newWidth
        self.height_ = newHeight

        # Compute new square sizes
        squareW = math.floor((newWidth - 2 * DELTA_W - STATS_FRAME_WIDTH) / ROW_COUNT)
        squareH = math.floor((newHeight - MENUBAR_HEIGHT - 2 * DELTA_H) / LINE_COUNT)

        if squareW < SQUARE_MIN or squareH < SQUARE_MIN :
            self.extSquareWidth_ = SQUARE_MIN

        # Use the smallest !
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * EXT_BORDER_THICK

        # Update elements'font
        if self.sElement_ is not None:
            fontSize = int(ELT_FONT_SIZE * self.intSquareWidth_ / SQUARE_SIDE)
            self.sElement_.setFont(ELT_FONT_NAME, fontSize)
            self.sElement_.moveTo((self.extSquareWidth_ - fontSize) / 2, 0)

    # Draw window's background and grid's borders
    #
    def _drawBackground(self):
        self._int_drawBackground()

    def _int_drawBackground(self, a = None, b= None, c= None, d = None, e = None):

        if self.win_ is None :
            return (False, False, None, None)

        # background ...
        self.win_.fill(self.BK_COLOUR)

        if 0 != self.extSquareWidth_ :

            # thin borders ...
            #
            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = DELTA_W + row * self.extSquareWidth_
                    y = MENUBAR_HEIGHT + DELTA_H + line * self.extSquareWidth_
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + self.extSquareWidth_))
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + self.extSquareWidth_), (x + self.extSquareWidth_, y + self.extSquareWidth_))

            # ... large ext. borders
            #
            lSquare = self.extSquareWidth_ * 3
            for line in range(3):
                for row in range(3):
                    x = DELTA_W + row * lSquare
                    y = MENUBAR_HEIGHT + DELTA_H + line * lSquare
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + lSquare), EXT_BORDER_THICK)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + lSquare), (x + lSquare, y + lSquare), EXT_BORDER_THICK)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y + lSquare), (x + lSquare, y), EXT_BORDER_THICK)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y), (x, y), EXT_BORDER_THICK)

        self._int_update()

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #
    def _updateGrid(self, elements, limit):
        # On réaffiche toute la grille ...
        self._int_draw(elements)

    # Show text message (on top of the grid)
    #
    def _showMessage(self, message, elements):
        if self.sMessage_:
            # Remove previous message (if any)
            self._clearMessage(elements)

            # Draw on the specific surface
            self.sMessage_.setText(message, self.TXT_COLOUR, self.BK_COLOUR)

            # start blinking
            self.sMessage_.setVisible()
            self.sMessage_.startTimer()

    # Clear the current text message
    #
    def _clearMessage(self, elements):
        if self.sMessage_:
            # Remove events
            pygame.event.get(self.sMessage_.eventID())

            self.sMessage_.erase()
            self.sMessage_.killTimer()

            # redraw ...
            self._int_refresh(elements)

 # EOF
