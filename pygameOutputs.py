# coding=UTF-8
#
#   File        :   pygameOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of pygameOutputs and textSurfcace objects
#                   Displays the grid using PYGame
#                   
#                   pygameOutputs inherits outputs class
#

import pygame, math

from outputs import outputs
from ownExceptions import sudokuError
from pointer import pointer

# 
# Internal constants
#

# Positions and dimensions in pixels
#
SQUARE_SIDE             = 60   # Initial external size of a square element

STATS_FRAME_WIDTH       = 100  # Width in pixels of stats'frame

SQUARE_MIN              = 10   # Minimal square size

DELTA_X                 = 10   # Grid offsets
DELTA_Y                 = 10

EXT_BORDER_THICK        = 3    # Thickness of external border

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
class textSurface(object):

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
        return True if self.surface_ else False

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
        return (self.position_[0], self.position_[1], self.surface_.get_width(), self.surface_.get_height())

    # Current position
    def position(self):
        return self.position_
    
    # Change position
    def moveTo(self, x, y):
        self.position_ = (x,y)

    # Dimensions
    #
    def getWidth(self):
        return 0 if not self.isVisible() else self.surface_.get_width()
    def getHeight(self):
        return 0 if not self.isVisible() else self.surface_.get_height()

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
class pygameOutputs(outputs):

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
    MOUSE_BUTTON_LEFT   = 1
    MOUSE_BUTTON_MIDDLE = 2 # ???
    MOUSE_BUTTON_RIGHT  = 3
    
    # Change element value
    REMOVE_VALUE        = pygame.K_DELETE
    VALUE_DEC           = pygame.K_PAGEDOWN
    VALUE_INC           = pygame.K_PAGEUP

    # Set value
    VALUE_1             = pygame.K_1
    VALUE_9             = pygame.K_9

    VALUE_KB_1          = pygame.K_KP0  # from keypad
    VALUE_KB_9          = pygame.K_KP9

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

    # Text message
    sMessage_ = None
        
    # Construction
    #
    def __init__(self):
        self._start()
        self._drawBackground()

    def _start(self, ) :
        
        self.initDone_ = False
        self.mode_ = self.MODE_EDIT + self.MODE_BROWSEFOLDER

        # Init. the lib.
        try:
            rets = pygame.init()
        except:
            raise sudokuError("PYGame initialization error - Mayb you should reinstall PYGame")

        if 0 != rets[1] :
            raise sudokuError("PYGame initialization error - PYGame returns " + str(rets[1]) + " error(s)")

        # PYGame init. is ok
        self.initDone_ = True
        
        # Default dimensions
        self.width_ = pointer.ROW_COUNT * SQUARE_SIDE + 2 * DELTA_X
        self.height_ = pointer.LINE_COUNT * SQUARE_SIDE + 2 * DELTA_Y
        self.extSquareWidth_ = SQUARE_SIDE
        self.intSquareWidth_ = SQUARE_SIDE - 2 * EXT_BORDER_THICK
        self.deltaW_ = DELTA_X
        self.deltaH_ = DELTA_Y
        
        # font for drawing elements
        self.sElement_ = textSurface(ELT_FONT_NAME, ELT_FONT_SIZE)
        self.sElement_.moveTo((SQUARE_SIDE - ELT_FONT_SIZE) / 2, 0)
        
        # window creation
        #self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.NOFRAME)
        #self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.SCALED)
        pygame.display.set_caption('sudoSolver')

        # fileName displays
        self.sFileName_ = textSurface(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.sFileName_.moveTo(FILE_FONT_POS_X, FILE_FONT_POS_Y)
        self.sFileName_.setEventID(pygame.USEREVENT + 1, DEF_MSG_HIDING_FREQ)   # event for text hiding

        # Messages
        self.sMessage_ = blinkingText(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.sMessage_.setEventID(pygame.USEREVENT + 2, DEF_BLINKING_FREQ)
   
    # Use GUI ?
    #
    def useGUI(self):
        return True
    
    # Display text
    #
    def displayText(self, text, information, elements):
        if True == information:
           super().displayText(text) 
        else:
            self._int_displayText(text, elements)

    def _int_displayText(self, text, elements):
        # Display text on top of the board
        self._showMessage(text, elements)
        self._int_refresh(elements)
    
    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents):
        return self._int_waitForEvent(elements, allEvents)
        
    def _int_waitForEvent(self, elements, allEvents):
        finished = False
        while not finished:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN :
                finished = True
            elif event.type == pygame.VIDEORESIZE:
                
                # Update members
                self._onResizeWindow(event.w, event.h)
                
                # Resize the surface
                self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)

                # Draw bkgrnd & lines ...
                self._int_drawBackground()

                # ... and the grid's content
                if not None == elements:
                    self._int_draw(elements)
                
                # returns all events ?
                if True == allEvents:
                    finished = True
            # New filename to display
            elif event.type == self.sFileName_.eventID():
                # Erase the name
                self.sFileName_.erase()  
                self._int_refresh(elements)

                # kill the timer
                self.sFileName_.killTimer()
                if True == allEvents:
                    finished = True
            # Blinking text
            elif event.type == self.sMessage_.eventID():
                # Change text visibility
                self.sMessage_.changeVisibility()
                self._refresh(elements)
                if True == allEvents:
                    finished = True

        return event
    
    # Check current/last event
    #
    def pollEvent(self):
        return self._int_pollEvent()

    def _int_pollEvent(self):
        event = pygame.event.poll()

        # turn keypad num keys into num keys
        if event.type == pygame.KEYDOWN and event.key >= pygame.K_KP1 and event.key <= pygame.K_KP9:
            event.key = pygame.K_1 + event.key - pygame.K_KP1

        return event
    
    # Mouse events and status
    #
    #   returns tuple (ButtonID or None, (xPos, yPos))
    #
    def mouseButtonStatus(self, event):
        return (self.MOUSE_BUTTON_NONE, (0,0)) if event is None else (event.button, event.pos)

    # Is a key pressed ?
    #
    #   returns the tuple (pressed?, key or None if not pressed)
    #
    def keyPressed(self, elements = None, allEvents = False):
        return self._int_keyPressed(elements, allEvents)

    def _int_keyPressed(self, elements = None, allEvents = False):
        evt = pygame.event.poll()
        pressed = (evt.type == pygame.QUIT or evt.type == pygame.KEYDOWN)
        return (pressed, evt if pressed else None)    

    # Set/change the current grid's filename
    #
    def setGridName(self, fileName):
        self._int_setGridName(fileName)
    
    def _int_setGridName(self, fileName):
        super().setGridName(fileName)

        self.sFileName_.setText(fileName, self.TXT_COLOUR, outputs.BK_COLOUR_FILENAME)
        
        # erase this name after a while ...
        self.sFileName_.startTimer()

    # Mouse position
    #
    def mousePosition(self, pos):
        return (int((pos[0] - EXT_BORDER_THICK - self.deltaW_) / self.extSquareWidth_) , int((pos[1] - EXT_BORDER_THICK - self.deltaH_) / self.extSquareWidth_))
    
    # Draw the whole grid
    #
    def draw(self, elements):
        self._int_draw(elements)
    
    def _int_draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):    
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
        if 0 == self.extSquareWidth_ :
            return
        
        # top-left corner position
        x = self.deltaW_ + row * self.extSquareWidth_ + EXT_BORDER_THICK
        y = self.deltaH_ + line * self.extSquareWidth_ + EXT_BORDER_THICK
        
        # Erase background
        pygame.draw.rect(self.win_, bkColour, (x, y, self.intSquareWidth_, self.intSquareWidth_))

        # The value (if valid)
        if None != value:
            self.sElement_.setText(str(value), txtColour)
            
            # Center the text
            dx = (self.intSquareWidth_ - self.sElement_.getWidth()) / 2
            dy = (self.intSquareWidth_ - self.sElement_.getHeight()) / 2
            self.win_.blit(self.sElement_.surface(), (x + dx, y + dy))

    # Update the window
    #
    def update(self):
        self._int_update()
    
    def _int_update(self):
        # Display filename ?
        if self.sFileName_ and self.sFileName_.isValid():
            # draw the name
            self.win_.blit(self.sFileName_.surface(), self.sFileName_.position())
        
        # A message ?
        if self.sMessage_ and self.sMessage_.isVisible():
            x = int((self.width_ - self.sMessage_.getWidth())/2)
            y = int((self.height_ - self.sMessage_.getHeight())/2)

             # draw the text
            self.win_.blit(self.sMessage_.surface(), (x,y))
        
        pygame.display.update()
    
    # Close the display
    def close(self):
        if self.initDone_:
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
        squareW = math.floor((newWidth - 2 * DELTA_X - STATS_FRAME_WIDTH) / pointer.ROW_COUNT)
        squareH = math.floor((newHeight - 2 * DELTA_Y) / pointer.LINE_COUNT)

        if squareW < SQUARE_MIN or squareH < SQUARE_MIN :
            self.extSquareWidth_ = SQUARE_MIN
        
        # Use the smallest !
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * EXT_BORDER_THICK
        
        # top-left grid position
        self.deltaW_ = math.floor((newWidth - pointer.ROW_COUNT * self.extSquareWidth_) / 2)
        self.deltaH_ = math.floor((newHeight - pointer.LINE_COUNT * self.extSquareWidth_) / 2)

        # Update elements'font
        fontSize = int(ELT_FONT_SIZE * self.intSquareWidth_ / SQUARE_SIDE)
        self.sElement_.setFont(ELT_FONT_NAME, fontSize)
        self.sElement_.moveTo((self.extSquareWidth_ - fontSize) / 2, 0) 


    # Draw window's background and grid's borders
    #
    def _drawBackground(self):
        self._int_drawBackground()

    def _int_drawBackground(self):
        
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
            self.sMessage_.setText(message, self.TXT_COLOUR, outputs.BK_COLOUR)

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