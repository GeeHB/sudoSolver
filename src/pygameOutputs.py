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


    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements:list[element]):
        pass

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



 # EOF
