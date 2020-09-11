# coding=UTF-8
#
#   File     :   pyOutputs.py
#
#   Author      :   JHB
#
#   Description :   Définition of pyOutputs and textSurfcace objects
#                   Displays the grid using PYGame
#                   
#                   pyOutputs inherits outputs class
#
#   Version     :   0.1.24
#
#   Date        :   2020-09-08
#

from outputs import outputs

from ownExceptions import reachedEndOfList, sudokuError
from element import element, elementStatus
from pointer import pointer

import pygame
import math

# 
# Internal conts.
#

# Positions and dimensions
#
SQUARE_SIDE         = 60   #  Initial external size of a square element

SQUARE_MIN          = 10   # Minimal square size

DELTA_X             = 10    # Grid offsets
DELTA_Y             = 10

EXT_BORDER_WIDTH    = 3     # Width of external border

# Elements'text font
#
ELT_FONT_NAME           = 'Herculanum,Papyrus,Helvetica'    # The first font in the list ...
ELT_FONT_SIZE           = 35                                # default size

FILE_FONT_NAME          = 'Helvetica,Arial'                 # Grid's name display 
FILE_FONT_SIZE          = 25
FILE_FONT_POS_X         = 35
FILE_FONT_POS_Y         = 5

ERASE_NAME_AFTER        = 2000  # in ms

#
# textSurface - "subsurface" containig a single line of text
#
class textSurface(object):
    # Members
    surface_    = None
    position_   = (0,0)    
    font_       = None      # Font used for drawing the text
    eventID_    = 0         # Event ID - optionnal

    # Construction
    def __init__(self, fontName, fontSize):
        self.setFont(fontName, fontSize)

    # Valid ?
    def isValid(self):
        return True if self.surface_ else False

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
        self.surface_ = self.font_.render(text, 1, txtColour, bkColour)

    # Erases the surface
    def erase(self):
        if self.surface_ :
            del self.surface_
            self.surface_ = None

    # Dimensions & position
    #
    
    # Bounding rectangle
    def rect(self):
        return (self.position_[0], self.position_[1], self.surface_.get_width(), self.surface_.get_height())

    # Current position
    def position(self):
        return self.position_
    
    # Change position
    def moveTo(self, x, y):
        self.position_ = (x,y)

    # Event ID
    def eventID(self):
        return self.eventID_

    def setEventID(self, id):
        self.eventID_ = id

#
# pyOutputs - Display sudoku's grid using PYGame library
#
class pyOutputs(outputs):

    EVT_KEYDOWN         = pygame.KEYDOWN
    EVT_QUIT            = pygame.QUIT
    
    # PYGame keys
    #
    MOVE_LEFT           = pygame.K_LEFT
    MOVE_RIGHT          = pygame.K_RIGHT
    MOVE_UP             = pygame.K_UP
    MOVE_DOWN           = pygame.K_DOWN
    
    VALUE_DEC           = pygame.K_e        # Change element value
    VALUE_INC           = pygame.K_r

    EDIT_CANCEL         = pygame.K_ESCAPE
    EDIT_QUIT_AND_SAVE  = pygame.K_RETURN
    
    # Members
    #
    win_            = None     # My window
    
    width_          = 0        # Window's dimensions
    height_         = 0
    
    
    intSquareWidth_ = 0        # Internal dims of an element
    extSquareWidth_ = 0        # Ext. dims 
    
    deltaW_         = 0        # Grid's offsets
    deltaH_         = 0
    
    # Elements'values drawing
    sElement_ = None

    # Display the grid name
    sFileName_       = None
        
    # Construction
    #
    def __init__(self, showDetails = False):
        
        self.mode_ = self.MODE_EDIT + self.MODE_BROWSEFOLDER

        # Init. the lib.
        rets = pygame.init()
        if 0 != rets[1] :
            raise sudokuError("PYGame initialization error - PYGame returns " + str(rets[1]) + " error(s)")

        # Dimensions
        self.width_ = pointer.ROW_COUNT * SQUARE_SIDE + 2 * DELTA_X
        self.height_ = pointer.LINE_COUNT * SQUARE_SIDE + 2 * DELTA_Y
        self.extSquareWidth_ = SQUARE_SIDE
        self.intSquareWidth_ = SQUARE_SIDE - 2 * EXT_BORDER_WIDTH
        self.deltaW_ = DELTA_X
        self.deltaH_ = DELTA_Y
        
        # font for drawing elements
        self.sElement_ = textSurface(ELT_FONT_NAME, ELT_FONT_SIZE)
        self.sElement_.moveTo((SQUARE_SIDE - ELT_FONT_SIZE) / 2, 0)
        
        # window creation
        self._setWindowSize()
        pygame.display.set_caption('sudoSolver')

        self._drawBackground()

        # fileName displays
        self.sFileName_ = textSurface(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.sFileName_.moveTo(FILE_FONT_POS_X, FILE_FONT_POS_Y)
        self.sFileName_.setEventID(pygame.USEREVENT + 1)   # event for text hidding
   
    # Display text
    #
    def displayText(self, text, information):
        if True == information:
           super().displayText(text) 
        else:
            # Display text on top of the board
            print(text)
    
    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents):
        # On attend l'appui sur une touche ou la retaille de la fenêtre
        finished = False
        while not finished:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN :
                finished = True
            elif event.type == pygame.VIDEORESIZE:
                # Update members
                self._onResizeWindow(event.w, event.h)
                
                # Resize the surface
                self._setWindowSize()

                # Draw bkgrnd & lines ...
                self._drawBackground()

                # ... and the grid's content
                if not None == elements:
                    self.draw(elements)
                
                # returns all events ?
                if True == allEvents:
                    finished = True
            elif event.type == self.sFileName_.eventID():
                # Erase the name
                self.sFileName_.erase()                    
                self._drawBackground()
                self.draw(elements)
                self.update()

                pygame.time.set_timer(self.sFileName_.eventID(), 0)
                if True == allEvents:
                    finished = True

        return event

    # Set/change the current grid's filename
    #   overloaded
    def setGridName(self, fileName):
        super().setGridName(fileName)

        self.sFileName_.setText(fileName, self.TXT_COLOUR, outputs.BK_COLOUR_FILENAME)
        
        # erase this name after a while ...
        pygame.time.set_timer(self.sFileName_.eventID(), ERASE_NAME_AFTER)

    
    # Draw all the content of the current grid
    #
    def draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):    
                currentElement = elements[position.index()]
                self.drawSingleElement(row, line, currentElement.value(), currentElement.isOriginal(), self.BK_COLOUR, self.TXT_COLOUR)

                # next element ...
                position+=1

        self.update()

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row, line, value, highLighted, bkColour, txtColour):
        
        # too small to be drawn ?
        if 0 == self.extSquareWidth_ :
            return
        
        # top-left corner position
        x = self.deltaW_ + row * self.extSquareWidth_ + EXT_BORDER_WIDTH
        y = self.deltaH_ + line * self.extSquareWidth_ + EXT_BORDER_WIDTH
        
        # Erase background
        pygame.draw.rect(self.win_, bkColour, (x, y, self.intSquareWidth_, self.intSquareWidth_))

        # The value (if valid)
        if not None == value:
            if highLighted : 
                #font.set_bold(True)
                txtColour = self.HILITE_COLOUR
            
            self.sElement_.setText(str(value), txtColour)
            offset = self.sElement_.position()
            self.win_.blit(self.sElement_.surface(), (x + offset[0], y + offset[0]))

    # Update the window
    #
    def update(self):
        # Display filename ?
        if self.sFileName_ and self.sFileName_.isValid():
            # draw the name
            self.win_.blit(self.sFileName_.surface(), self.sFileName_.position())
        pygame.display.update()
    
    def close(self):
        # close the display
        pygame.display.quit()

    #
    # "private" methods
    #

    # Handle window's resize
    #
    def _onResizeWindow(self, newWidth, newHeight):

        self.width_ = newWidth
        self.height_ = newHeight

        # Compute new square sizes 
        squareW = math.floor((newWidth - 2 * DELTA_X) / pointer.ROW_COUNT)
        squareH = math.floor((newHeight - 2 * DELTA_Y) / pointer.LINE_COUNT)

        if squareW < SQUARE_MIN or squareH < SQUARE_MIN :
            self.extSquareWidth_ = SQUARE_MIN
        
        # Use the smallest !
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * EXT_BORDER_WIDTH
        
        # top-left grid position
        self.deltaW_ = math.floor((newWidth - pointer.ROW_COUNT * self.extSquareWidth_) / 2)
        self.deltaH_ = math.floor((newHeight - pointer.LINE_COUNT * self.extSquareWidth_) / 2)

        # Update elements'font
        fontSize = int(ELT_FONT_SIZE * self.intSquareWidth_ / SQUARE_SIDE)
        self.sElement_.setFont(ELT_FONT_NAME, fontSize)
        self.sElement_.moveTo((self.extSquareWidth_ - fontSize) / 2, 0) 


    # Draw window's background and grid'borders
    #
    def _drawBackground(self):
        
        # background ...
        self.win_.fill(self.BK_COLOUR)

        if not 0 == self.extSquareWidth_ : 
            
            # thin borders ...
            #
            for line in range(pointer.LINE_COUNT):
                for row in range(pointer.ROW_COUNT):
                    x = self.deltaW_ + row * self.extSquareWidth_
                    y = self.deltaH_ + line * self.extSquareWidth_
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + self.extSquareWidth_))
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + self.extSquareWidth_), (x + self.extSquareWidth_, y + self.extSquareWidth_))

            # ... large ext. borders
            #
            lSquare = self.extSquareWidth_ * 3
            for line in range(3):
                for row in range(3):
                    x = self.deltaW_ + row * lSquare
                    y = self.deltaH_ + line * lSquare
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + lSquare), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + lSquare), (x + lSquare, y + lSquare), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y + lSquare), (x + lSquare, y), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y), (x, y), EXT_BORDER_WIDTH)

        self.update()

    # Change the size of themain window
    #
    def _setWindowSize(self):
        # Updates dimensions
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)
        
    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #  
    def _update(self, elements, limit):
        # On réaffiche toute la grille ...
        self.draw(elements) 

 # EOF