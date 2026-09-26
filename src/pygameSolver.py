# coding=UTF-8
#
#   File        :   pygameSolver.py
#
#   Author      :   GeeHB
#
#   Description :   draw sudoku using pygame library
#
import copy
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

import GUIConsts
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


# Events frequencies in ms
#
DEF_MSG_HIDING_FREQ     = 2000  # Hide the filename
DEF_BLINKING_FREQ       = 750   # blinking freq. in ms

# solverApp - Abstract class for application
#
class pygameSolverApp(solver.solverApp):
    # Constructor
    #
    def __init__(self, params : options):
        super().__init__(params)

        # Init. the lib.
        rets = pygame.init()
        if 0 != rets[1] :
            raise sudokuError(f"PYGame initialization error - PYGame returns {rets[1]!r} error(s)")

        self.solver_ : pygameSolver = pygameSolver(params)  # Create sudoku solver

    # GUI initialization
    #
    @override
    def initialize(self):
        self.solver_.initialize()

    # Start drawings / UI
    #
    @override
    def start(self):
        self.solver_.startUI()

    # End drawings
    #
    @override
    def end(self):
        self.solver_.end()

        pygame.display.quit()
        pygame.quit()


#
# textSurface - "subsurface" containig a single line of text
#
class textSurface:
    # Construction
    def __init__(self, fontName:str, fontSize:int):
        # Members
        self.surface_ : pygame.Surface | None = None
        self.position_ : tuple[int,int] = (0,0)
        self.font_ : pygame.font.Font | None = None      # Font used for drawing the text
        self.eventID_ : int = 0         # Event ID - optionnal
        self.eventFreq_ : int = 0
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

    def __init__(self, params : options):
        solver.solver.__init__(self, params)    # Call parent's constructor

        self.win_  = None     # My window
        self.mode_ :statusbits.statusBits = statusbits.statusBits()       # Display mode

        self.sElement_ : textSurface | None = None      # single value
        self.sFileName_ : textSurface | None = None
        self.sMessage_ : blinkingText | None = None
        self.params_.center = True

    #
    # Methods from solver
    #

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self.initialized = False
        self.mode_.assign(self.MODE_EDIT + self.MODE_BROWSEFOLDER)

        # PYGame init. is ok
        self.initialized = True

        # font for drawing elements
        fontSize = int(GUIConsts.ELT_FONT_SIZE * self.intSquareWidth_ / GUIConsts.SQUARE_SIDE_BASE)
        self.sElement_ = textSurface(GUIConsts.ELT_FONT_NAME, fontSize)
        self.sElement_.moveTo(int(int(self.extSquareWidth_) - fontSize / 2), 0)

        # Main window creation
        myDict = systeminfos.getSystemInformations()
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.SCALED if myDict is not None and myDict[systeminfos.KEY_WM] == systeminfos.WM_CHROMEOS else pygame.RESIZABLE )

        pygame.display.set_caption(APP_SHORT_NAME)

        # fileName displays
        self.sFileName_ = textSurface(GUIConsts.FILE_FONT_NAME, GUIConsts.FILE_FONT_SIZE)
        self.sFileName_.moveTo(GUIConsts.FILE_FONT_POS_X, GUIConsts.FILE_FONT_POS_Y)
        self.sFileName_.setEventID(pygame.USEREVENT + 1, DEF_MSG_HIDING_FREQ)   # event for text hiding

        # Messages
        self.sMessage_ = blinkingText(GUIConsts.FILE_FONT_NAME, GUIConsts.FILE_FONT_SIZE)
        self.sMessage_.setEventID(pygame.USEREVENT + 2, DEF_BLINKING_FREQ)
        self._draw_background()

    # Start the sudoku (browsing, editing or solving)
    #
    @override
    def startUI(self):
        try:
            if self.params_.browseFolder:
                self.filename = self._browse(self.params_.folderName_)
                if 0 == len(self.params_.fileName_):
                    return
            else:
                self.sudoku_.load(
                    self.params_.fileName_, not self.params_.execMode_.isSet(options.EXEC_EDIT)
                )

            self.draw()

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
                        self.draw()
                        self._waitForEvent(allEvents=False)

                # ... and then try to resolve
                found, self.stats_.bruteAttempts_, self.stats_.bruteDuration_ = (
                    self.resolve()
                )

                # Display the solution (if any)
                self.draw()
                self._displayText("Press a key to quit", False)

                time.sleep(1)
                self._waitForEvent(allEvents=False)

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
        if self.initialized :
            # Close text objects
            if self.sFileName_ is not None:
                self.sFileName_.end()
            if self.sMessage_ is not None:
                self.sMessage_.end()

            self.initialized = False

    #
    #  drawings
    #

    # Draw background, frames and borders
    #
    @override
    def _draw_background(self):
        if self.win_ is not None:
            self.win_.fill(self.colours_[self.ColourID.ID_BK].other)
            if 0 != self.extSquareWidth_ :
                # thin borders ...
                #
                for line in range(LINE_COUNT):
                    for row in range(ROW_COUNT):
                        x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + self.offsets_[0]
                        y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + self.offsets_[1]
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x, y),
                            (x, y + self.extSquareWidth_))
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x, y + self.extSquareWidth_),
                            (x + self.extSquareWidth_, y + self.extSquareWidth_))

                # ... large ext. borders
                #
                lSquare = self.extSquareWidth_ * 3
                for line in range(3):
                    for row in range(3):
                        x = GUIConsts.DELTA_W + row * lSquare + self.offsets_[0]
                        y = GUIConsts.DELTA_H + line * lSquare + self.offsets_[1]
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x, y),
                            (x, y + lSquare), GUIConsts.EXT_BORDER_THICK)
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x, y + lSquare),
                            (x + lSquare, y + lSquare), GUIConsts.EXT_BORDER_THICK)
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x + lSquare, y + lSquare),
                            (x + lSquare, y), GUIConsts.EXT_BORDER_THICK)
                        pygame.draw.line(self.win_, self.colours_[self.ColourID.ID_BORDER].other,
                            (x + lSquare, y),
                            (x, y), GUIConsts.EXT_BORDER_THICK)

            #self.update()
        #else:
            #return (False, False, None, None)

    # Update the whole window
    #
    @override
    def update(self):
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

    # Refresh the whole window
    #
    def _refresh(self):
        self._draw_background()
        if len(self.sudoku_.elements_) > 0:
            self.draw()
        else:
            self.update()

    # Display text
    #
    def _displayText(self, text:str, information:bool):
        if information:
            print(text)
        else:
            # Display text on top of the board
            self._showMessage(text)
            self._refresh()

    # Draw/erase a single element and its background
    #
    @override
    def _draw_singleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int):
        # too small to be drawn ?
        if self.win_ is None or 0 == self.extSquareWidth_ :
            return

        # top-left corner position
        x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[0]
        y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[1]

        # Erase background
        pygame.draw.rect(self.win_, self.colours_[bkColourID].other, (x, y, self.intSquareWidth_, self.intSquareWidth_))

        # The value (if valid)
        if value is not None and self.sElement_ is not None:
            self.sElement_.setText(str(value), self.colours_[txtColourID].other)

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
            self.sMessage_.setText(message,
                self.colours_[self.ColourID.ID_TXT].other,
                self.colours_[self.ColourID.ID_BK].other)

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
    @override
    def setFileName(self, fileName:str, create:bool = False):
        solver.solver.setFileName(self, fileName, create)

        if self.sFileName_ is not None :
            self.sFileName_.setText(fileName,
                self.colours_[self.ColourID.ID_TXT].other,
                self.colours_[self.ColourID.ID_BK_FILENAME].other)

            # erase this name after a while ...
            self.sFileName_.startTimer()

    #
    # Events
    #

    # Handle window's resize
    #
    @override
    def newWindowSize(self, newWidth:int, newHeight:int):
        solver.solver.newWindowSize(self, newWidth, newHeight)

        # Update elements'font
        if self.sElement_ is not None:
            self.sElement_.setFont(GUIConsts.ELT_FONT_NAME, self.fontSize_)
            self.sElement_.moveTo(int((self.extSquareWidth_ - float(self.fontSize_))/2), 0)

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
                    self.newWindowSize(self.win_.get_width(), self.win_.get_height())

                    # ... and the array's content
                    self.draw(re_draw_background=True)

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
                    self.fromFile(currentFile)
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
        self.edition_.clear(solver.editStatus.EDIT_CONTINUE)    # let's go !

        while not self.edition_.status_.isSet(solver.editStatus.EDIT_STOP):
            # if sel. changed, erase previously selected element
            self._edit_updatePos(
                None if self.edition_.status_.isSet(solver.editStatus.EDIT_NO_REDRAW) else self.edition_.prevPos_,
                self.edition_.currentPos_,
            )

            self.edition_.forward()

            # Wait for an event
            event = self._pollEvent()

            # By a mouse click ?
            if self.EVT_MOUSEBUTTONDOWN == event.type:
                button, pos = self._mouseButtonStatus(event)
                if button == self.MOUSE_BUTTON_LEFT:
                    _ = self.edition_.currentPos_.moveTo(pos=self.mousePosition(pos))
            else:
                # With the keyboard
                if self.EVT_KEYDOWN == event.type:
                    match event.key:
                        case self.MOVE_LEFT:
                            self.edition_.currentPos_.decRow()
                        case self.MOVE_RIGHT:
                            self.edition_.currentPos_.incRow()
                        case self.MOVE_UP:
                            self.edition_.currentPos_.decLine()
                        case self.MOVE_DOWN:
                            self.edition_.currentPos_.incLine()
                        case key if key in range(
                            self.VALUE_1, self.VALUE_9 + 1
                        ):
                            self._edit_setValue(key - self.VALUE_1 + 1)
                        case self.VALUE_DEC:
                            self._edit_decValue()
                        case self.VALUE_INC:
                            self._edit_incValue()
                        case self.REMOVE_VALUE:
                            self._edit_removeValue()
                        case self.EDIT_CANCEL:
                            print(f"Avant : {self.edition_.status_.value_}")
                            self.edition_.status_.set(solver.editStatus.EDIT_ESCAPED)
                            print(f"Après : {self.edition_.status_.value_}")
                            print("bye bye")
                        case self.EDIT_QUIT_AND_SAVE:
                            self.edition_.status_.set(solver.editStatus.EDIT_STOP)
                            print("On sort")
                        case _:
                            pass

                elif event.type == self.EVT_QUIT:
                    self.edition_.status_.set(solver.editStatus.EDIT_ESCAPED)

        escaped = self.edition_.status_.isSet(solver.editStatus.EDIT_ESCAPE)
        if not escaped:
            value : int | None = self.sudoku_.elements_[self.edition_.currentPos_.index()].num
            if value is not None:
                self._draw_singleElement(
                    self.edition_.currentPos_.row(),
                    self.edition_.currentPos_.line(),
                    value,
                    self.ColourID.ID_BK,
                    self.ColourID.ID_HILITE,
                    )
                self.update()

        # Saves changes or exit
        return (
            escaped,
            ((self.sudoku_.save() is not None) if self.edition_.status_.isSet(solver.editStatus.EDIT_MODIFIED) else True)
            if not escaped
            else False,
        )

    # Update array during edition
    #
    @override
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        solver.solver._edit_updatePos(self, prevPos, currentPos)
        self.update()

    # Convert colour objects from ownColour to pygameColor
    #
    @override
    def convertColours(self):
        for id in range(len(self.colours_)):
            self.colours_[id].other = pygame.Color(
                self.colours_[id].r,
                self.colours_[id].g,
                self.colours_[id].b,
                self.colours_[id].a)

# EOF
