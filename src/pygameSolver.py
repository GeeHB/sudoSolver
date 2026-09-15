# coding=UTF-8
#
#   File        :   pygameSolver.py
#
#   Author      :   GeeHB
#
#   Description :   sudoSolver object
#
import copy
import math
import os
import sys
import time
from typing import override

try :
    import pygame
except ModuleNotFoundError:
    print("pygame not installed - pip install pygame | sudo apt/dnf install python(3)-pygame")
    sys.exit(0)
import pygame.event

import solver
from element import element
from options import (
    APP_AUTHOR_SHORT,
    APP_NAME,
    APP_SHORT_NAME,
    FILE_EXPORT_EXTENSION,
    options,
)
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

DELTA_W                 = 10   # Offsets
DELTA_H                 = 10

EXT_BORDER_THICK        = 3    # Thickness of external border

MENUBAR_HEIGHT          = 32

# Elements'text font sizes (in pixels) and names
#
ELT_FONT_NAME           = 'Herculanum,Papyrus,Helvetica'    # The first font in the list ...
ELT_FONT_SIZE           = 35                                # default size

FILE_FONT_NAME          = 'Helvetica,Arial'                 # for the filename
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
# pygameSolver - Display sudoku's array using PYGame library
#
class pygameSolver(solver.solver):
    # Keys & events
    #
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

    # Display modes
    #
    MODE_DEFAULT:int        = statusbits.STATUS_NONE
    MODE_EDIT:int           = 1
    MODE_BROWSEFOLDER:int   = 2

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

    # Edition status
    #
    EDIT_CONTINUE:int = statusbits.STATUS_NONE
    EDIT_MODIFIED:int = 1  # The sudoku has been modified (at least once)
    EDIT_STOP:int = 2  # Stop edition
    EDIT_ESCAPE:int = 4  # Escape edition
    EDIT_ESCAPED:int = EDIT_STOP | EDIT_ESCAPE
    EDIT_NOREDRAW:int = 8  # don't redraw at previous pos value

    def __init__(self, params : options):
        super().__init__(params)

        self.win_            = None     # My window
        self.width_ :int = 0        # Window's dimensions
        self.height_ : int = 0
        self.intSquareWidth_ :int = 0        # Internal dims of an element
        self.extSquareWidth_ :int = 0        # Ext. dims
        self.editStatus_:statusbits.statusBits = statusbits.statusBits(self.EDIT_CONTINUE)

        # Elements'values drawing
        self.sElement_ : textSurface | None = None

        self.mode_ :statusbits.statusBits = statusbits.statusBits()       # Display mode

        self.keyHandler_ = None

        # Display the sudoku's name
        self.sFileName_ : textSurface | None       = None

        # Text message
        self.sMessage_ : blinkingText | None = None

    #
    # Methods from solver
    #

    # GUI initialization
    #
    @override
    def initialize(self):
        self.initialized = False
        self.mode_.assign(self.MODE_EDIT + self.MODE_BROWSEFOLDER)

        # Init. the lib.
        rets = pygame.init()

        if 0 != rets[1] :
            raise sudokuError(f"PYGame initialization error - PYGame returns {rets[1]!r} error(s)")

        # PYGame init. is ok
        self.initialized = True

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
        self._drawBackground()

    # Start the sudoku (browsing, editing or solving)
    #
    @override
    def start(self):
        try:
            if self.params_.browseFolder:
                self.params_.fileName_ = self._browse(self.params_.folderName_)
                if 0 == len(self.params_.fileName_):
                    return
            else:
                self.sudoku_.load(
                    self.params_.fileName_, not self.params_.execMode_.isSet(options.EXEC_EDIT)
                )

            self._draw()

            # Edition
            if self.params_.execMode_.isSet(options.EXEC_EDIT):
                # Succefully edited ?
                escape, saved = self._edit()
                if escape == True or saved == False:
                    # Escaped or error while saving
                    self.params_.execMode_.remove(options.EXEC_SOLVE)

            # Search for the solution
            #
            if self.params_.execMode_.isSet(options.EXEC_SOLVE):
                if not self.params_.execMode_.isSet(options.EXEC_EDIT):
                    self._displayText("Press a key to start the solver", False)
                    self._waitForEvent(allEvents=False)

                # Obvious values first ...
                if self.params_.obviousValues:
                    self.stats_.obvValues_, self.stats_.obvDuration_ = self.sudoku_.findObviousValues()

                    if self.stats_.obvValues_ > 0:
                        self._displayText(
                            f"Found {self.stats_.obvValues_!r} obvious values", False
                        )
                        self._draw()
                        self._waitForEvent(allEvents=False)

                # ... and then try to resolve
                found, escaped, self.stats_.bruteAttempts_, self.stats_.bruteDuration_ = (
                    self.sudoku_.resolve()
                )

                # Display the solution (if any)
                self._draw()
                self._displayText("Press a key to quit", False)

                time.sleep(1)
                self._waitForEvent(allEvents=False)

                if escaped:
                    print("Resolution process canceled")
                else:
                    # Export the solution ?
                    if self.params_.exportSolution:
                        comments : list[str] = []
                        comments.append(" ")
                        comments.append(f" Source file : {self.params_.fileName_}")
                        comments.append(" ")
                        comments.append(
                            f"Solved by {APP_AUTHOR_SHORT}::{APP_NAME} in {round(self.stats_.bruteDuration_, 2)!r} sec."
                        )
                        comments.append(" ")

                        if self.sudoku_.save(True, comments) is not None:
                            print(
                                f"Solution successfully saved in {self.params_.fileName_}{FILE_EXPORT_EXTENSION}"
                            )

                self.end()

                # A few stats.
                if found:
                    self.showStats()
                else:
                    print(f"No solution found for '{self.params_.fileName_}'")
        except sudokuError as e:
            print(e)
        except IndexError:
            print("Too many lines in the file", file=sys.stderr)
        except KeyboardInterrupt:
            print("Canceled by user")

    # End drawings
    #
    @override
    def end(self):
        if self.initialized and self.sFileName_ is not None and self.sMessage_ is not None:
            # Close text objects
            self.sFileName_.end()
            self.sMessage_.end()

            # close the display
            pygame.display.quit()
            pygame.quit()
            self.initialized = False

    #
    #  drawings
    #

    def _drawBackground(self):
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

        self._update()

    # Update the whole window
    #
    def _update(self):
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

    def _flip(self):
        pygame.display.flip()

    # Refresh the whole window
    #
    def _refresh(self):
        self._drawBackground()
        if len(self.sudoku_.elements_) > 0:
            self._draw()
        else:
            self._update()

    # Display text
    #
    def _displayText(self, text:str, information:bool):
        if information:
            print(text)
        else:
            # Display text on top of the board
            self._showMessage(text)
            self._refresh()

    # Draw the whole array
    #
    def _draw(self):
        position : pointer = pointer(gameMode = False)
        for line in range(LINE_COUNT):
            for row in range(ROW_COUNT):
                currentElement = self.sudoku_.elements_[position.index()]
                value : int | None = currentElement.num
                if value is not None:
                    self._drawSingleElement(row, line, value, self.BK_COLOUR, self.HILITE_COLOUR if currentElement.isOriginal() else self.OBVIOUS_COLOUR if currentElement.isObvious() else self.TXT_COLOUR)

                # next element ...
                position+=1

        self._update()

    # Draw/erase a single element and its background
    #
    def _drawSingleElement(self, row:int, line:int, value:int | None, bkColour:pygame.Color, txtColour:pygame.Color):
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

    # Show text message (on top of the sudoku)
    #
    def _showMessage(self, message : str):
        if self.sMessage_:
            # Remove previous message (if any)
            self._clearMessage()

            # Draw on the specific surface
            self.sMessage_.setText(message, self.TXT_COLOUR, self.BK_COLOUR)

            # start blinking
            self.sMessage_.setVisible()
            self.sMessage_.startTimer()

    # Clear the current text message
    #
    def _clearMessage(self):
        if self.sMessage_:
            # Remove events
            pygame.event.get(self.sMessage_.eventID())

            self.sMessage_.erase()
            self.sMessage_.killTimer()

            # redraw ...
            self._refresh()

    # Set/change the current array's filename
    #
    def _setFileName(self, fileName:str, create:bool = False):
        # the file must exists
        if False == create and False == os.path.isfile(fileName):
            raise sudokuError(fileName +  " is not a file")
        self.params_.fileName_ = fileName

        if self.sFileName_ is not None :
            self.sFileName_.setText(fileName, self.TXT_COLOUR, self.BK_COLOUR_FILENAME)

            # erase this name after a while ...
            self.sFileName_.startTimer()

    # Load a sudoku stored in a file
    #
    #   return True if sudoku has been successfully loaded
    #
    def _fromFile(self, fileName : str, nameOnArray:bool=True) -> bool:
        self.sudoku_.empty()

        try:
            self.sudoku_.load(fileName, True, False)
        except UnicodeDecodeError:
            return False
        except sudokuError as se:
            print(f"Sudoku Error : {se.message_}")
            return False

        if nameOnArray:
            self._setFileName(fileName)

        self._drawBackground()
        self._draw()
        self._update()

        return True

    #
    # Events
    #

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

    # Wait for an event
    #
    def _waitForEvent(self, allEvents:bool) -> pygame.event.Event:
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
                    self._drawBackground()

                    # ... and the array's content
                    self._draw()

                    # returns all events ?
                    if True == allEvents:
                        finished = True

                # New filename to display
                elif self.sFileName_ is not None and event.type == self.sFileName_.eventID():
                    # Erase the name
                    self.sFileName_.erase()
                    self._refresh()

                    # kill the timer
                    self.sFileName_.killTimer()
                    if True == allEvents:
                        finished = True
                # Blinking text
                elif self.sMessage_ is not None and event.type == self.sMessage_.eventID():
                    # Change text visibility
                    self.sMessage_.changeVisibility()
                    self._refresh()
                    if True == allEvents:
                        finished = True
        return event

    # Check current/last event
    #
    def _pollEvent(self) -> pygame.event.Event:
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
    def _getEvents(self)->list[pygame.event.Event]:
        return pygame.event.get()

    # Mouse events and status
    #
    #   returns tuple (ButtonID or None, (xPos, yPos))
    #
    def _mouseButtonStatus(self, event : pygame.event.Event | None)->tuple[int|None, tuple[int, int]]:
        return (self.MOUSE_BUTTON_NONE, (0,0)) if event is None else (event.button, event.pos)

    # Is a key pressed ?
    #
    #   returns the tuple(pressed?, key or None if not pressed)
    #
    def _keyPressed(self, allEvents : bool = False) -> tuple[bool,pygame.event.Event | None]:
        evt = pygame.event.poll()
        valid : bool = (evt.type == pygame.QUIT or evt.type == pygame.KEYDOWN)
        return (True, evt) if valid else (False, None)

    # Mouse position
    #
    def _mousePosition(self, pos : tuple[int,int]):
         return (-1 if pos[0] < DELTA_W else int((pos[0] - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_), -1 if pos[1] < (MENUBAR_HEIGHT + DELTA_H) else int((pos[1] - MENUBAR_HEIGHT - EXT_BORDER_THICK - DELTA_W) / self.extSquareWidth_))

    #
    #  Edition & browsing
    #

    # Browse a folder (to find a sudoku file)
    #
    #  Returns the selected filename or ""
    def _browse(self, folderName:str)->str:
        if not os.path.isdir(folderName):
            raise sudokuError(f"{folderName} is not a valid folder")

        files : list[str] = []
        done:bool = not self._folderContent(folderName, files)
        prev:int = -1
        index:int = 0
        currentFile:str = ""
        maxIndex:int = len(files)
        clearFile:bool = False

        # Browse ...
        while not done:
            # update drawings ?
            if prev != index:
                currentFile = os.path.join(folderName, files[index])

                # load the file and update drawings
                try:
                    self._fromFile(currentFile)
                except sudokuError as e:
                    print(f"Sudoku Error : {e.message_}")
                except OSError as other:
                    # the file is not valid => remove it from the list
                    print(f"Invalid file : {other}")
                    _ = files.pop(index)
                    maxIndex -= 1

                prev = index

            if 0 == maxIndex:
                # Nothing left in the folder
                # return currentFile
                done = True

            index, done, clearFile = self._browseFolder_handleKeyBoard(index, maxIndex)

        return "" if clearFile else currentFile

    # Wait for keyboard event while browsing a folder
    #
    # Returns the tuple(new index, done?, clearfile?)
    def _browseFolder_handleKeyBoard(self, index:int, maxIndex:int)->tuple[int,bool,bool]:
        clearFile : bool = False
        done : bool = False

        event : pygame.event.Event = self._waitForEvent(allEvents=True)

        if event.type == self.EVT_KEYDOWN:
            if self.MOVE_RIGHT == event.key:
                index += 1
                if index >= maxIndex:
                    index = 0
            else:
                if self.MOVE_LEFT == event.key:
                    index -= 1
                    if index < 0:
                        index = maxIndex - 1
                else:
                    # Cancel
                    if self.EDIT_CANCEL == event.key:
                        done = True
                        clearFile = True
                    else:
                        # Choose the sudoku from file (for edition or solving)
                        if self.EDIT_QUIT_AND_SAVE == event.key:
                            done = True
        elif event.type == self.EVT_QUIT:
            done = True
            clearFile = True

        return (index, done, clearFile)

    # List of sudokus in a folder
    #   fill the {files} with {folder} content
    #
    #   return True if the list is not empty, False in all other cases
    def _folderContent(self, folder:str, files:list[str])->bool:
        files.clear()

        # Folder content
        if len(folder) > 0:
            # Only this folder
            for _, _, fileNames in os.walk(folder):
                files.extend(fileNames)
                break

        # No solution files in the list !
        for file in files:
            _, fileExt = os.path.splitext(file)
            if FILE_EXPORT_EXTENSION == fileExt:
                # remove the file from the list
                files.remove(file)

        files.sort()
        return len(files) > 0

    # Edit / modify the sudoku's array
    #
    #   Returns the tuple of booleans : (escaped ?, sudoku saved (or successfully edited) ?)
    #
    def _edit(self) -> tuple[bool, bool]:
        currentPos : pointer = pointer(gameMode=False)  # current position
        prevPos : pointer | None =  None  # previous pos (if erase needed)
        self.editStatus_.value = self.EDIT_CONTINUE

        while not self.editStatus_.isSet(self.EDIT_STOP):
            # if sel. changed, erase previously selected element
            self._edit_updatePos(
                None if self.editStatus_.isSet(self.EDIT_NOREDRAW) else prevPos,
                currentPos,
            )
            prevPos = copy.deepcopy(currentPos)   # // copy constructor
            self.editStatus_.remove(self.EDIT_NOREDRAW)

            # Wait for an event
            event = self._pollEvent()

            # By a mouse click ?
            if self.EVT_MOUSEBUTTONDOWN == event.type:
                button, pos = self._mouseButtonStatus(event)
                if button == self.MOUSE_BUTTON_LEFT:
                    currentPos.moveTo(pos=self._mousePosition(pos))
            else:
                # With the keyboard
                if self.EVT_KEYDOWN == event.type:
                    match event.key:
                        case self.MOVE_LEFT:
                            currentPos.decRow()
                        case self.MOVE_RIGHT:
                            currentPos.incRow()
                        case self.MOVE_UP:
                            currentPos.decLine()
                        case self.MOVE_DOWN:
                            currentPos.incLine()
                        case key if key in range(
                            self.VALUE_1, self.VALUE_9 + 1
                        ):
                            self._edit_setValue(
                                currentPos, key - self.VALUE_1 + 1
                            )
                        case self.VALUE_DEC:
                            self._edit_decValue(currentPos)
                        case self.VALUE_INC:
                            self._edit_incValue(currentPos)
                        case self.REMOVE_VALUE:
                            self._edit_removeValue(currentPos)
                        case self.EDIT_CANCEL:
                            self.editStatus_.set(self.EDIT_ESCAPED)
                        case self.EDIT_QUIT_AND_SAVE:
                            self.editStatus_.set(self.EDIT_STOP)
                        case _:
                            pass

                elif event.type == self.EVT_QUIT:
                    self.editStatus_.set(self.EDIT_ESCAPED)

        escaped = self.editStatus_.isSet(self.EDIT_ESCAPE)
        if not escaped:
            value : int | None = self.sudoku_.elements_[currentPos.index()].num
            if value is not None:
                self._drawSingleElement(
                    currentPos.row(),
                    currentPos.line(),
                    value,
                    self.BK_COLOUR,
                    self.HILITE_COLOUR,
                )
                self._update()

        # Saves changes or exit
        return (
            escaped,
            ((self.sudoku_.save() is not None) if self.editStatus_.isSet(self.EDIT_MODIFIED) else True)
            if not escaped
            else False,
        )

    # Update array during edition
    #
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        if prevPos is not None:
            # if sel. changed, erase previously selected element
            self._drawSingleElement(
                prevPos.row(),
                prevPos.line(),
                self.sudoku_.elements_[prevPos.index()].num,
                self.BK_COLOUR,
                self.HILITE_COLOUR,
            )

            # Hilight the new value
            self._drawSingleElement(
                currentPos.row(),
                currentPos.line(),
                self.sudoku_.elements_[currentPos.index()].num,
                self.SEL_BK_COLOUR,
                self.HILITE_COLOUR,
            )
            self._update()

    # (try to) set a value
    #
    def _edit_setValue(self, pos: pointer, val: int):
        if self.sudoku_.checkValue(pos, val):
            self.sudoku_.elements_[pos.index()].setValue(val, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Decrease value
    #
    def _edit_decValue(self, pos: pointer):
        val : int | None = self.sudoku_.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findPreviousValue(pos, val)
        if newVal != val:
            self.sudoku_.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Inc value
    #
    def _edit_incValue(self, pos: pointer):
        val : int | None = self.sudoku_.elements_[pos.index()].num
        if val is None:
            val = 0

        newVal : int = self.sudoku_.findNextValue(pos, val)
        if newVal != val:
            self.sudoku_.elements_[pos.index()].setValue(newVal, element.STATUS_ORIGINAL, True)
            self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

    # Remove current value
    #
    def _edit_removeValue(self, pos: pointer):
        self.sudoku_.elements_[pos.index()].setValue(0, element.STATUS_ORIGINAL, True)
        self.editStatus_.set(self.EDIT_NOREDRAW | self.EDIT_MODIFIED)

# EOF
