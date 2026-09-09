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
from typing import override

try :
    import pygame
except ModuleNotFoundError:
    print("pygame not installed - pip install pygame | sudo apt/dnf install python(3)-pygame")
    sys.exit(0)
import pygame.event

from element import element
from options import APP_SHORT_NAME, options, stats
from ownExceptions import sudokuError
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
    pointer,
)
from sharedTools import (
    statusbits,
    systeminfos,
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
# textSurface - "subsurface" containig a single line of text
#
class textSurface:
    # Construction
    def __init__(self, fontName:str, fontSize:int):
        # Members
        self.surface_ : pygame.Surface | None   = None
        self.position_ : tuple[int,int]  = (0,0)
        self.font_ : pygame.font.Font | None       = None      # Font used for drawing the text
        self.eventID_ : int    = 0         # Event ID - optionnal
        self.eventFreq_ : int  = 0
        self.setFont(fontName, fontSize)

    # Valid ?
    def isValid(self)->bool:
        return bool(self.surface_)

    # Visible ?
    def isVisible(self)->bool:
        return self.isValid()

    # My surface
    def surface(self)->pygame.Surface | None:
        return self.surface_

    # Create / change the font
    def setFont(self, fontName:str, fontSize:int):
        if self.font_:
            del self.font_
        self.font_ = pygame.font.SysFont(fontName, fontSize)

    # Create a surface with the associated text
    def setText(self, text : str, txtColour : pygame.Color, bkColour : pygame.Color | None = None):
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
    def rect(self)->tuple[int,int,int,int]:
        if self.surface_ is not None :
            return (self.position_[0], self.position_[1], self.surface_.get_width(), self.surface_.get_height())
        return (0,0,0,0)

    # Current position
    def position(self)->tuple[int,int]:
        return self.position_

    # Change position
    def moveTo(self, x:int, y:int):
        self.position_ = (x,y)

    # Dimensions
    #
    def getWidth(self)->int:
        if self.surface_ is not None :
            return 0 if not self.isVisible() else self.surface_.get_width()
        return 0
    def getHeight(self)->int:
        if self.surface_ is not None :
            return 0 if not self.isVisible() else self.surface_.get_height()
        return 0

    # Event ID
    #
    def eventID(self)->int:
        return self.eventID_
    def setEventID(self, id:int, freq:int):
        self.eventID_ = id
        self.eventFreq_ = freq

    # Timer
    #
    def startTimer(self):
        pygame.time.set_timer(self.eventID(), self.eventFreq_)
    def killTimer(self):
        pygame.time.set_timer(self.eventID(), 0)
    def frequency(self)->int:
        return self.eventFreq_

#
# blinkingText - "subsurface" containig a single line of blinking text
#
class blinkingText(textSurface):
    # Construction
    def __init__(self, fontName : str, fontSize : int):
        super().__init__(fontName, fontSize)
        self.visible_ : bool = True


    # Text visibility
    #
    @override
    def isVisible(self)->bool:
        return self.visible_ if self.isValid() else False
    def setVisible(self, visible:bool = True):
        self.visible_ = visible
    def changeVisibility(self)->bool:
        self.visible_ = not self.visible_
        return self.visible_

#
# pygameOutputs - Display sudoku's grid using PYGame library
#
class pygameOutputs:

    EVT_KEYDOWN:int         = pygame.KEYDOWN
    EVT_QUIT:int            = pygame.QUIT

    # PYGame keys
    #
    MOVE_LEFT:int           = pygame.K_LEFT
    MOVE_RIGHT:int          = pygame.K_RIGHT
    MOVE_UP:int             = pygame.K_UP
    MOVE_DOWN:int           = pygame.K_DOWN

    # Mouse click
    EVT_MOUSEBUTTONDOWN:int = pygame.MOUSEBUTTONDOWN

    # Mouse button ID
    MOUSE_BUTTON_NONE:int   = 0
    MOUSE_BUTTON_LEFT:int   = 1
    MOUSE_BUTTON_MIDDLE:int = 2 # ???
    MOUSE_BUTTON_RIGHT:int  = 3

    # Change element value
    REMOVE_VALUE:int        = pygame.K_DELETE
    REMOVE_VALUE_BIS:int    = pygame.K_BACKSPACE

    VALUE_DEC:int           = pygame.K_PAGEDOWN
    VALUE_INC:int           = pygame.K_PAGEUP

    # Set value
    VALUE_1:int             = pygame.K_1
    VALUE_9:int             = pygame.K_9

    VALUE_KPAD_1:int         = pygame.K_KP1  # from keypad
    VALUE_KPAD_9:int         = pygame.K_KP9

    EDIT_CANCEL:int         = pygame.K_ESCAPE
    EDIT_QUIT_AND_SAVE:int  = pygame.K_RETURN

    #  App colours
    #
    BORDER_COLOUR:pygame.Color = pygame.Color(81, 154, 186)
    BK_COLOUR:pygame.Color     = pygame.Color(230, 230, 255)
    BK_COLOUR_FILENAME:pygame.Color  = pygame.Color(220, 220, 245)
    TXT_COLOUR:pygame.Color = pygame.Color(64, 64, 64)
    HILITE_COLOUR:pygame.Color = pygame.Color(248, 128, 112)
    OBVIOUS_COLOUR      = BORDER_COLOUR

    SEL_BK_COLOUR : pygame.Color = pygame.Color(50, 50, 255)
    SEL_TXT_COLOUR : pygame.Color = pygame.Color(255, 255, 255)

    # Display modes
    #
    MODE_DEFAULT:int        = statusbits.STATUS_NONE
    MODE_EDIT:int           = 1
    MODE_BROWSEFOLDER:int   = 2

    # Construction
    #
    def __init__(self):
        self.win_            = None     # My window

        self.width_ :int = 0        # Window's dimensions
        self.height_ : int = 0

        self.intSquareWidth_ :int = 0        # Internal dims of an element
        self.extSquareWidth_ :int = 0        # Ext. dims

        # Elements'values drawing
        self.sElement_ : textSurface | None = None

        self.mode_ :statusbits.statusBits = statusbits.statusBits()       # Display mode
        self.gridFileName_ : str | None = None

        self.keyHandler_ = None

        # Display the grid name
        self.sFileName_ : textSurface | None       = None

        # Text message
        self.sMessage_ : blinkingText | None = None

    def startUI(self):
        self._start()
        self.drawBackground()

    def _start(self) :
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
        self.sElement_.moveTo(int(int(self.extSquareWidth_) - fontSize / 2), 0)

        # Main window creation
        myDict = systeminfos.getSystemInformations()
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.SCALED if myDict is not None and myDict[systeminfos.KEY_WM] == systeminfos.WM_CHROMEOS else pygame.RESIZABLE )

        pygame.display.set_caption(APP_SHORT_NAME)

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
    def allowEdition(self)->bool:
        return self.mode_.isSet(self.MODE_EDIT)

    # Is this display mode compatible with forlder browsing ?
    def allowFolderBrowsing(self)->bool:
        return self.mode_ .isSet(self.MODE_BROWSEFOLDER)

    # Show resolution stats
    #
    #   Print stats on console (by default)
    #
    # can be overloaded
    def showStats(self, params: options, sStats : stats):
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
    def displayText(self, text:str, information:bool, elements:list[element]):
        if True == information:
            # By default, text is displayed on the console
            print(text)
        else:
            self._int_displayText(text, elements)

    def _int_displayText(self, text:str, elements:list[element]):
        # Display text on top of the board
        self._showMessage(text, elements)
        self._int_refresh(elements)

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements:list[element]):
        pass

    # Wait for an event
    #
    def waitForEvent(self, elements:list[element], allEvents:bool) -> pygame.event.Event:
        return self._int_waitForEvent(elements, allEvents)

    def _int_waitForEvent(self, elements:list[element] | None, allEvents:bool)  -> pygame.event.Event:
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
                    if elements is not None:
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
    def getEvents(self)->list[pygame.event.Event]:
        return pygame.event.get()

    # Mouse events and status
    #
    #   returns tuple (ButtonID or None, (xPos, yPos))
    #
    def mouseButtonStatus(self, event : pygame.event.Event | None)->tuple[int|None, tuple[int, int]]:
        return (self.MOUSE_BUTTON_NONE, (0,0)) if event is None else (event.button, event.pos)

    # Is a key pressed ?
    #
    #   returns the tuple(pressed?, key or None if not pressed)
    #
    def keyPressed(self, elements : list[element] | None = None, allEvents : bool = False) -> tuple[bool,pygame.event.Event | None]:
        return self._int_keyPressed(elements, allEvents)

    def _int_keyPressed(self, elements : list[element] | None = None, allEvents : bool = False) -> tuple[bool,pygame.event.Event | None]:
        evt = pygame.event.poll()
        valid = (evt.type == pygame.QUIT or evt.type == pygame.KEYDOWN)
        return (True, evt) if valid else (False, None)

    # Set/change the current grid's filename
    #
    def setGridName(self, fileName:str, create:bool = False):
        self._int_setGridName(fileName, create)

    def _int_setGridName(self, fileName:str, create:bool = False):
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
    def mousePosition(self, pos : tuple[int,int]):
        return (-1 if pos[0] < DELTA_W else int((pos[0] - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_), -1 if pos[1] < (MENUBAR_HEIGHT + DELTA_H) else int((pos[1] - MENUBAR_HEIGHT - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_))

    # Draw the whole grid
    #
    def draw(self, elements : list[element]):
        self._int_draw(elements)

    def _int_draw(self, elements : list[element]):
        position = pointer(gameMode = False)
        for line in range(LINE_COUNT):
            for row in range(ROW_COUNT):
                currentElement = elements[position.index()]
                value : int | None = currentElement.num
                if value is not None:
                    self._int_drawSingleElement(row, line, value, self.BK_COLOUR, self.HILITE_COLOUR if currentElement.isOriginal() else self.OBVIOUS_COLOUR if currentElement.isObvious() else self.TXT_COLOUR)

                # next element ...
                position+=1

        self._int_update()

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row:int, line:int, value:int | None, bkColour:pygame.Color, txtColour:pygame.Color):
        self._int_drawSingleElement(row, line, value, bkColour, txtColour)

    def _int_drawSingleElement(self, row:int, line:int, value:int | None, bkColour:pygame.Color, txtColour:pygame.Color):
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
    def _refresh(self, elements : list[element] | None):
        self._int_refresh(elements)

    def _int_refresh(self, elements : list[element] | None):
        if elements is not None :
            self._int_drawBackground()
            if elements:
                self._int_draw(elements)
            else:
                self._int_update()

    # Handle window's resize
    #
    def _onResizeWindow(self, newWidth:int, newHeight:int):

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
            self.sElement_.moveTo(int((self.extSquareWidth_ - float(fontSize))/2), 0)

    # Draw window's background and grid's borders
    #
    def drawBackground(self):
        self._int_drawBackground()

    #def _int_drawBackground(self, a = None, b= None, c= None, d = None, e = None):
    def _int_drawBackground(self):
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
    def _updateGrid(self, elements : list[element], limit : pointer):
        # On réaffiche toute la grille ...
        self._int_draw(elements)

    # Show text message (on top of the grid)
    #
    def _showMessage(self, message : str, elements : list[element]):
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
    def _clearMessage(self, elements : list[element]):
        if self.sMessage_:
            # Remove events
            pygame.event.get(self.sMessage_.eventID())

            self.sMessage_.erase()
            self.sMessage_.killTimer()

            # redraw ...
            self._int_refresh(elements)

 # EOF
