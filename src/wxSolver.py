# coding=UTF-8
#
#   File        :   wxSolver.py
#
#   Author      :   GeeHB
#
#   Description :   draw sudoku using the wxPython library
#                   Fedora : sudo dnf install python3-wxpython4
#
import math
import sys
from enum import IntEnum
from typing import override

try :
    import wx  # pyright: ignore[reportMissingTypeStubs]
    import wx.adv
    from wx.core import NullFont
    #from wx.core import GUIEventLoop
except ModuleNotFoundError:
    print("wxPython library is not installed")
    sys.exit(0)

import appStrings
import element
import GUIConsts
import GUITheme
import menuConsts
import solver
from options import (
    APP_SHORT_NAME,
    FILE_EXTENSION,
    arrayComplexity,
    options,
)
from pointer import (
    ARRAY_SIZE,
    LINE_COUNT,
    ROW_COUNT,
    VALUE_MAX,
    pointer,
)
from sharedTools import statusbits


# Edition modes
#
class wxEditionMode(IntEnum):
    MODE_NONE = 0
    MODE_CREATION = 1
    MODE_RESOLUTION = 2

# wxMainFrame
#   abstract class
#
#   Allow interactions with contained toolbar/sidebar and canvas panel
#
class wxMainFrame(wx.Frame):

    # App. states
    #

    # Edition mode changed
    def modeChanged(self, mode:wxEditionMode):
        pass

    # Theme just changed
    def themeChanged(self):
        pass

    # count of elements changed
    def countChanged(self):
        pass

    # Hypothesis / tag management
    #
    def hyp_onSelectColour(self, colID:int):
        pass
    def hyp_onReject(self, colours: list[element.hypColour]):
        pass
    def hyp_onValidate(self, colours: list[element.hypColour]):
        pass

    # End of edition
    #
    def onStopEdition(self, canceled:bool = False):
        pass

# wxOwnPanel - abstract class base for all panel objects
#
class wxOwnPanel(wx.Panel):
    def __init__(self, parent: wxMainFrame):
        super().__init__(parent)
        self.parent_: wxMainFrame = parent

    def initialize(self):
        pass

    # Theme just changed
    def themeChanged(self):
        pass

# wxSolverApp - Abstract class for application
#
class wxSolverApp(wx.App, solver.solverApp):
    # Constructor
    #
    def __init__(self, params: options):
        wx.Log.SetLogLevel(wx.LOG_Error)  # pyright: ignore[reportUnknownMemberType]
        wx.App.__init__(self)  # pyright: ignore[reportUnknownMemberType]
        solver.solverApp.__init__(self, params)

        self.mainFrame_ : wxSolverFrame = wxSolverFrame(params)

    # GUI initialization
    #
    @override
    def initialize(self):
        self.mainFrame_.initialize()

    # Start drawings / UI
    #
    @override
    def start(self):
        self.mainFrame_.Show()
        self.MainLoop()  # pyright: ignore[reportUnknownMemberType]

    # End drawings
    #
    @override
    def end(self):
        self.mainFrame_.end()

# wxSolverCanvas - Canvas using wxPython lib
#
class wxSolverCanvas(wxOwnPanel, solver.solver):
    #
    #  Array states
    #
    ARRAY_NEW : int = 0
    ARRAY_MODIFIED : int = 1
    ARRAY_EDITING : int = 2
    ARRAY_SOLVING : int = 4

    #
    #  key codes
    #
    KEY_MOVE_LEFT:int = wx.WXK_LEFT
    KEY_MOVE_RIGHT:int = wx.WXK_RIGHT
    KEY_MOVE_UP:int = wx.WXK_UP
    KEY_MOVE_DOWN:int = wx.WXK_DOWN

    # Change element value
    KEY_REMOVE_VALUE:int = wx.WXK_DELETE
    KEY_REMOVE_VALUE_BIS:int = wx.WXK_BACK

    KEY_VALUE_DEC:int = wx.WXK_PAGEDOWN
    KEY_VALUE_DEC_PAD:int = wx.WXK_NUMPAD_PAGEDOWN
    KEY_VALUE_INC:int = wx.WXK_PAGEUP
    KEY_VALUE_INC_PAD:int = wx.WXK_NUMPAD_PAGEUP

    # Set value
    KEY_VALUE_1:int = 325 #ord('1')
    KEY_VALUE_9:int = 333 #ord('9')

    KEY_VALUE_KPAD_1:int = wx.WXK_NUMPAD1
    KEY_VALUE_KPAD_9:int = wx.WXK_NUMPAD1

    KEY_ENTER: int = wx.WXK_RETURN
    KEY_NUM_ENTER:int = wx.WXK_NUMPAD_ENTER

    EDIT_CANCEL:int = wx.WXK_ESCAPE

    # Constructor
    #
    def __init__(self, parent: wxMainFrame, params : options):
        wxOwnPanel.__init__(self, parent)
        solver.solver.__init__(self, params)

        self.state_: statusbits.statusBits = statusbits.statusBits(self.ARRAY_NEW)

        # Display
        self.memDC_: wx.MemoryDC | None = None # all display are made in a memory DC
        self.elementFont_: wx.Font
        self.directDraw_:bool = False
        self.clientSize_: wx.Size = wx.Size(0,0)
        self.textOffsets_: list[tuple[wx.Size,wx.Size]] = []  # for text in array (0 : element size, 1 : help size)

        # Help matrix
        self.helpVisible_:bool = False
        self.helpCanvasFontSize_:int = 0
        self.helpIntSquareWidth_:int = 0
        self.helpOffsets_:tuple[int,int] = (0,0)

        # Timers (selection and notification)
        self.selectedTimer_:wx.Timer = wx.Timer(self, GUIConsts.TIMER_ID_SELECTED)
        self.notifyTimer_:wx.Timer = wx.Timer(self, GUIConsts.TIMER_ID_NOTIFYING)
        self.notify_:bool = False
        self.notifyCount_:int = 0

        self.menuThemesID_:dict[str,int] = {}

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self._menu_create()

        # Associate event to handlers
        #
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  # pyright: ignore[reportUnknownMemberType]

        #self.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonDown)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_LEFT_UP, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLButtonDClick)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_RIGHT_UP, self.OnRButtonUp)  # pyright: ignore[reportUnknownMemberType]

        self.Bind(wx.EVT_MENU, self.OnMenu)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_TIMER, self.OnTimer) # pyright: ignore[reportUnknownMemberType]

        self.SetFocus()
        self.Show()

    # End drawings
    #
    @override
    def end(self):
        self._notify_stop(True)
        self._edit_stop(True)

        self._draw_freeMemoryDC()


    # Set/change the current array's filename
    #
    @override
    def setFilename(self, fileName:str | None, create:bool = False):
        if fileName is not None:
            solver.solver.setFilename(self, fileName, create)

            title : str = APP_SHORT_NAME
            if len(fileName) > 0:
                title = title + " - " + fileName

            self.parent_.SetTitle(title)

    #
    # Event handlers
    #

    # Click on a menu item
    #
    def OnMenu(self, event:wx.MenuEvent):
        menuId = event.GetId()

        # From the contextual menu ?
        if self._menu_handleContextualItems(menuId):
            self._edit_selChanged()
            return

        # Other menu items
        match menuId:
            case menuConsts.ID_CREATE_EMPTY | menuConsts.ID_CREATE_EASY | menuConsts.ID_CREATE_MEDIUM | menuConsts.ID_CREATE_HARD :
                self._menu_fileNew(menuId)
            case wx.ID_OPEN:
                self._menu_fileOpen()
            case wx.ID_SAVE:
                self._menu_fileSave()

            case menuConsts.ID_DISPLAY_CENTER:
                actual:bool = self.params_.center
                self.params_.center = not actual

                self._draw_newClientSize(self.width_, self.height_)     # compute new dims
                self.draw_update()

            case menuConsts.ID_DISPLAY_HELP:
                self.helpVisible_ = not self.helpVisible_
                self._draw_newClientSize(self.width_, self.height_)     # compute new dims
                self._theme_fontChanged()
                self.draw_update()

            case menuConsts.ID_EDIT_UNDO:
                self._edit_undo()
            case menuConsts.ID_EDIT_MODIFY:
                self._menu_editOrResolve(edit = True)
            case menuConsts.ID_EDIT_DONE:
                self.sudoku_.hyp_acceptAll()
                self._edit_stop()
                self.edition_.creating = False
            case menuConsts.ID_EDIT_CANCEL:
                self._edit_cancel()
                self.edition_.creating = False

            case menuConsts.ID_SOLVE_MANUAL:
                self._menu_editOrResolve(edit = False)
            case menuConsts.ID_SOLVE_OBVIOUS:
                self._menu_findOviousValues()
            case menuConsts.ID_SOLVE_RESOLVE_SINGLE:
                    self._menu_resolveSingleThread()
            case menuConsts.ID_SOLVE_RESOLVE_MULTI:
                    self._menu_resolve_multiThreaded()
            case menuConsts.ID_SOLVE_REVERT:
                    self._menu_revertArray()

            case menuConsts.ID_HYP_VALIDATE:
                self._hyp_validate()
            case menuConsts.ID_HYP_REJECT:
                self._hyp_reject()

            case wx.ID_EXIT:
                self._menu_fileExit()
            case _:
                pass

        # Change theme ?
        if menuId in self.menuThemesID_.values():
           keys:list[str] = [k for k, v in self.menuThemesID_.items() if v == menuId]
           self._theme_changeByName(keys[0])

    # Keyboard events
    #
    def OnKeyDown(self, event :  wx.KeyEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            self._edit_array(event)
            return

        event.Skip()  # Allow other handlers to process the key

    # User press left button
    #
    """
    def OnLButtonDown(self, event : wx.MouseEvent):
        newPos: tuple[int,int] = self._mouse_translatePosition(pos=(event.x, event.y))
        print(f"Position : {newPos}")
        if newPos[0] != -1 :
            position:pointer = pointer()
            position.moveTo(pos=newPos)
            print(self.sudoku_.elements_[position.index()])

        event.Skip()  # Allow other handlers to process the key
    """

    # User clicked  with left button
    #
    def OnLButtonUp(self, event : wx.MouseEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            newPos: tuple[int,int,int] = self._mouse_translatePosition(pos=(event.x, event.y))
            #print(f"Click on {newPos}")
            match newPos[0]:
                case solver.ownZone.ZONE_ARRAY:
                    self.edition_.move()
                    if  self.edition_.currentPos_.moveTo(pos=(newPos[1], newPos[2])):   # click on the array
                        self._edit_selChanged()

                case solver.ownZone.ZONE_HELP_MATRIX:
                    value:int = 1 + 3 * newPos[2] + newPos[1]   # Value in the help matrix
                    #print(f"At {newPos} : {value}")
                    if -1 == self._edit_setValue(value)  :
                        self._edit_setValue(0)  # click on empty proposal
                    self.parent_.countChanged()
                    self._draw_helpMatrix_ex()
                    self._draw_selectedElement()    # update selected item (don't wait for 'blink')

                case _:
                    event.Skip()  # Allow other handlers to process the event

    # Double click with left button -> start edition or resolution
    #
    def OnLButtonDClick(self, event : wx.MouseEvent):
        if self.sudoku_.isOk() and not self.edition_.editing :
            clickPos : tuple[int, int, int] = self._mouse_translatePosition(pos=(event.x, event.y))
            if clickPos[0] == solver.ownZone.ZONE_ARRAY:
                dlg = wx.MessageDialog(
                    self,
                    appStrings.STR_EDIT_OR_SOLVE,
                    appStrings.STR_EDITION,
                    wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION
                )

                dlg.SetYesNoLabels(menuConsts.IDS_SOLVE_RESOLVE, appStrings.STR_MODIFY)  # pyright: ignore[reportUnknownMemberType]
                result = dlg.ShowModal()

                match result:
                    case wx.ID_YES:
                        self._menu_editOrResolve(edit = False, row = clickPos[1], line = clickPos[2])
                    case wx.ID_NO:
                        self._menu_editOrResolve(edit = True, row = clickPos[1], line = clickPos[2])
                    case _:
                        pass

                dlg.Destroy()

    # User pressed the right button => display contextual menu
    #
    def OnRButtonUp(self, event : wx.MouseEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            self.edition_.move()
            clickPos : tuple[int, int, int] = self._mouse_translatePosition(pos=(event.x, event.y))
            if clickPos[0] == solver.ownZone.ZONE_ARRAY and self.edition_.currentPos_.moveTo(pos=(clickPos[1], clickPos[2])):
                self._edit_selChanged()

            # possible values
            values:list[int] =self.sudoku_.getAllowedValues(self.edition_.currentPos_)

            # Generate a contextual menu at mouse pos with all possible values
            popUp: wx.Menu = wx.Menu()
            popUp.Append(menuConsts.ID_POPUP_VALUES[9], menuConsts.IDS_POPUP_EMPTY)
            popUp.Enable(menuConsts.ID_POPUP_VALUES[9], not self.sudoku_[self.edition_.currentPos_.index_].isEmpty())
            for index in range(1,10):
                id = menuConsts.ID_POPUP_VALUES[index-1]
                popUp.Append(id, f"{index}")
                popUp.Enable(id, index in values)

            self.PopupMenu(popUp, event.GetPosition())
            popUp.Destroy()

            return

        event.Skip()  # Allow other handlers to process the event

    # Draw the canvas and its content
    #
    def OnPaint(self, event : wx.Event):
        if self.memDC_ is not None and self.memDC_.IsOk():
            bmpSize : wx.Size = self.memDC_.GetSize()
            paintDC = wx.PaintDC(self)
            paintDC.Blit(0, 0, bmpSize.width, bmpSize.height, self.memDC_, 0, 0)    # blit memory bitmap onto dc

    # Window's size just changed
    #
    def OnSize(self, event : wx.SizeEvent):
        self.clientSize_ = self.GetClientSize() # Size minus menu height
        self._draw_newClientSize(self.clientSize_.width, self.clientSize_.height)

        self._draw_freeMemoryDC()

        # Create memory DC with bitmap
        self._draw_startUp()

        self._theme_fontChanged()       # update with newly computed font size

        # Redraw the whole array
        self._draw_background()
        self.draw()

    # Timer notification
    #
    def OnTimer(self, event : wx.Event):
        match event.Id:
            case GUIConsts.TIMER_ID_SELECTED:
                self._draw_selectionBlink()

            case GUIConsts.TIMER_ID_NOTIFYING:
                self._notify_drawElements()

            case _ :
                event.Skip()

    #
    #  Drawings
    #

    @override
    def _draw_startUp(self):
        if self.memDC_ is None :
            bmp = wx.Bitmap()
            bmp.CreateWithDIPSize(self.clientSize_, self.GetDPIScaleFactor())
            self.memDC_ = wx.MemoryDC(bmp)

            self._theme_fontChanged()    # Apply theme
            self.memDC_.SetBackground(wx.Brush(self.theme_[GUITheme.colourID.ID_CANVAS_BK].other))
            self.memDC_.Clear()

    @override
    def _draw_end(self):
        if not self.directDraw_:
            self.Refresh()
        else:
            if self.memDC_ is not None and self.memDC_.IsOk():
                bmpSize : wx.Size = self.memDC_.GetSize()
                clientDC = wx.ClientDC(self)
                clientDC.Blit(0, 0, bmpSize.width, bmpSize.height, self.memDC_, 0, 0)    # blit memory bitmap onto dc

    # Draw background, frames and borders
    #
    @override
    def _draw_background(self):
        if self.memDC_ is not None and 0 != self.extSquareWidth_ :

            self.memDC_.Clear()

            # Sudoku
            #

            # thin borders ...
            pen = wx.Pen(self.theme_[GUITheme.colourID.ID_FRAME_BORDER].other, 1, wx.PENSTYLE_SOLID)
            self.memDC_.SetPen(pen)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = row * self.extSquareWidth_ + self.offsets_[0]
                    y = line * self.extSquareWidth_ + self.offsets_[1]
                    self.memDC_.DrawLine(x, y, x, y + self.extSquareWidth_)
                    self.memDC_.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            if self.helpVisible_:
                x = self.helpOffsets_[0]
                y = self.helpOffsets_[1]

                elementWidth = self.helpIntSquareWidth_ + 2 * GUIConsts.EXT_BORDER_THICK
                matrixWidth:int = 3 * elementWidth
                offset:int = 0
                for _ in range(4):
                    self.memDC_.DrawLine(x + offset, y, x + offset, y + matrixWidth) # Vert.
                    self.memDC_.DrawLine(x, y + offset, x + matrixWidth, y + offset) # Horz.
                    offset+=elementWidth

                self._draw_helpMatrix()

            # ... large ext. borders
            penLarge = wx.Pen(self.theme_[GUITheme.colourID.ID_FRAME_BORDER].other, GUIConsts.EXT_BORDER_THICK, wx.PENSTYLE_SOLID)
            self.memDC_.SetPen(penLarge)
            lSquare = self.extSquareWidth_ * 3

            for line in range(3):
                for row in range(3):
                    x = row * lSquare + self.offsets_[0]
                    y = line * lSquare + self.offsets_[1]
                    self.memDC_.DrawLine(x, y,x, y + lSquare)
                    self.memDC_.DrawLine(x, y + lSquare,x + lSquare, y + lSquare)
                    self.memDC_.DrawLine(x + lSquare, y + lSquare,x + lSquare, y)
                    self.memDC_.DrawLine(x + lSquare, y, x, y)

    # Draw the proposed values matrix
    #
    def _draw_helpMatrix(self):
        if self.memDC_ is not None and self.sudoku_.isOk():
            values : list[int] = self.sudoku_.getAllowedValues(self.edition_.currentPos_) if self.edition_.editing else []
            value:int = 0

            self.memDC_.SetFont(self.helpFont_) # use small font

            y = self.helpOffsets_[1] + GUIConsts.EXT_BORDER_THICK

            for _ in range(3):
                #x = self.width_ - 3 * (self.helpIntSquareWidth_ + GUIConsts.EXT_BORDER_THICK) - self.offsets_[0]   # stick to the right border
                x = self.helpOffsets_[0] + GUIConsts.EXT_BORDER_THICK
                for _ in range(3):
                    value+=1
                    self._draw_singleValue(self.memDC_,
                        value if value in values else 0,
                        x, y,
                        self.helpIntSquareWidth_,
                        GUITheme.colourID.ID_FRAME_BK_EVEN,
                        GUITheme.colourID.ID_DEFAULT_TXT,
                        1)
                    x+=(self.helpIntSquareWidth_ + 2 * GUIConsts.EXT_BORDER_THICK)
                y+=(self.helpIntSquareWidth_ + 2 * GUIConsts.EXT_BORDER_THICK)

            self.memDC_.SetFont(self.elementFont_)

    def _draw_helpMatrix_ex(self):
        self._draw_startUp()
        self._draw_helpMatrix()
        self._draw_end()

    # The window's size has changed
    #
    @override
    def _draw_newClientSize(self, newWidth:int, newHeight:int, boxWidth:int | None = None):
        if self.helpVisible_:
            boxWidth = math.floor((newWidth - 2 * GUIConsts.DELTA_W - GUIConsts.HELP_SPACE) / (ROW_COUNT + 2))
            solver.solver._draw_newClientSize(self, newWidth, newHeight, boxWidth)
            self.helpIntSquareWidth_ = math.floor(self.intSquareWidth_/GUIConsts.HELP_RATIO)

            # update vertical offset
            if self.params_.center :
                self.offsets_ = (GUIConsts.DELTA_W + math.floor((self.width_ - GUIConsts.HELP_SPACE - self.extSquareWidth_ * (2 + ROW_COUNT)) / 2), self.offsets_[1])

            # Help matrix position
            self.helpOffsets_ = (self.offsets_[0] + ROW_COUNT * self.extSquareWidth_ + GUIConsts.HELP_SPACE, self.offsets_[1] + GUIConsts.HELP_SPACE)
        else:
            solver.solver._draw_newClientSize(self, newWidth, newHeight)

    # Redraw selected element
    #
    def _draw_selectionBlink(self):
        self._draw_startUp()
        self._draw_selectedElement(self.edition_.changeSelectedStatus())
        self._draw_end()

    # Draw/erase a single element and its background
    #
    @override
    def _draw_singleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int, hypColourID:int):
        # too small to be drawn ?
        if self.memDC_ is None or 0 == self.extSquareWidth_ :
            return

        # top-left corner position
        x = row * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[0]
        y = line * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[1]

        self._draw_singleValue(self.memDC_, value, x, y, self.intSquareWidth_, bkColourID, txtColourID, 0)

        # Hypothesis/Tag ?
        if hypColourID != element.hypColour.NO_COLOUR:
            self._draw_singleElementTag(self.memDC_, x, y, hypColourID)

    # Draw/erase a single value (element or proposed value) and its background
    #
    def _draw_singleValue(self, memDC:wx.DC, value:int | None, x:int, y:int, squareWidth:int,bkColourID:int, txtColourID:int, ratioId:int = 0):
        # Erase background
        memDC.SetBrush(wx.Brush(self.theme_[bkColourID].other))
        memDC.SetPen(wx.TRANSPARENT_PEN)
        memDC.DrawRectangle(x, y, squareWidth, squareWidth)

        # The value (if valid)
        #
        #   the 'valid' font is already selected onto the DC !!!
        #
        if value is not None and value > 0:
            memDC.SetTextForeground(self.theme_[txtColourID].other)
            try:
                memDC.DrawText(str(value), x + self.textOffsets_[value-1][ratioId].x, y + self.textOffsets_[value-1][ratioId].y)
            except IndexError:
                print(f"IndexError - value = {value} - ratioId = {ratioId}")

    # Draw a coloured tag
    def _draw_singleElementTag(self, memDC:wx.DC, x:int, y:int, hypColourID:int):
        memDC.SetBrush(wx.Brush(self.theme_[hypColourID + GUITheme.colourID.ID_TAG_1 - 1].other))
        # Hypothesis/Tag ?
        if hypColourID != element.hypColour.NO_COLOUR:
            memDC.SetBrush(wx.Brush(self.theme_[hypColourID + GUITheme.colourID.ID_TAG_1 - 1].other))
            memDC.SetPen(wx.TRANSPARENT_PEN)

            radius = int(self.tagWidth_ / 2)

            if self.tagWidth_ == GUIConsts.TAG_MIN_SIZE:
                memDC.DrawCircle(
                    x + self.intSquareWidth_ - GUIConsts.TAG_PADDING - radius,
                    y + GUIConsts.TAG_PADDING + radius,
                    radius)
            else:
                points = [
                    (0, 0),
                    (0, self.tagWidth_ + radius),
                    (radius, self.tagWidth_),
                    (self.tagWidth_, self.tagWidth_+radius),
                    (self.tagWidth_, 0)
                ]

                memDC.DrawPolygon(  # pyright: ignore[reportUnknownMemberType]
                    points,
                    x + self.intSquareWidth_ - GUIConsts.TAG_PADDING - self.tagWidth_,
                    y + GUIConsts.TAG_PADDING)

    # Delete current memory DC
    def _draw_freeMemoryDC(self):
        if self.memDC_ :
            self.memDC_.SelectObject(wx.NullBitmap) # Free previous bitmap if any
            self.memDC_ = None

    # Start edition mode
    #
    @override
    def _edit_start(self, initPos:bool = True):
        if self.sudoku_.isModified():
            if wx.MessageBox(appStrings.STR_MODIFIED_ARRAY, appStrings.STR_CREATE,
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            if self.sudoku_.setOriginal():
                self.draw_update()

        self._notify_stop() # Don't forget to stop notification timer !
        super()._edit_start(initPos)

        self.state_.set(self.ARRAY_EDITING)
        self._menu_setItemsStates()

        # Anything to edit ?
        if len(self.sudoku_.elements_) == 0:
            self.sudoku_.empty()

        if initPos:
            self.edition_.clear()    # move to cursor to (0,0)
        else:
            self.edition_.selected = False

        self._draw_selectionBlink()
        if not self.selectedTimer_.IsRunning():
            self.selectedTimer_.Start(GUIConsts.TIMER_RATE_SELECTED)

    # End of edition mode
    #
    @override
    def _edit_stop(self, endApp:bool = False):
        if not self.state_.isSet(self.ARRAY_EDITING):
            return  # ??? <- no edition mode  to be stopped

        super()._edit_stop(endApp)

        if not endApp:
            self.state_.remove(self.ARRAY_EDITING)
            if self.edition_.modified:
                self.state_.set(self.ARRAY_MODIFIED)

            self._menu_setItemsStates()

            if self.selectedTimer_.IsRunning():
                self.selectedTimer_.Stop()

            self._draw_startUp()
            self._draw_selectedElement(False)
            self._draw_helpMatrix()
            self._draw_end()

            self.parent_.modeChanged(wxEditionMode.MODE_NONE)

    # Selected item has just changed
    #
    def _edit_selChanged(self):
        #self._edit_stop()
        self._edit_updatePos(self.edition_.prevPos_, self.edition_.currentPos_)
        #self._edit_start(False)

    # Edition of current array
    #
    def _edit_array(self, event: wx.KeyEvent):
        keyCode = event.GetKeyCode()
        self.edition_.move()
        match keyCode:
            case self.KEY_MOVE_LEFT:
                self.edition_.currentPos_.decRow()
            case self.KEY_MOVE_RIGHT:
                self.edition_.currentPos_.incRow()
            case self.KEY_MOVE_UP:
                self.edition_.currentPos_.decLine()
            case self.KEY_MOVE_DOWN:
                self.edition_.currentPos_.incLine()

            case self.KEY_VALUE_DEC | self.KEY_VALUE_DEC_PAD:
                if self._edit_decValue() : self.parent_.countChanged()
            case self.KEY_VALUE_INC | self.KEY_VALUE_INC_PAD:
                if self._edit_incValue() : self.parent_.countChanged()
            case self.KEY_REMOVE_VALUE:
                if self._edit_removeValue() : self.parent_.countChanged()

            case key if key in range(
                self.KEY_VALUE_1, self.KEY_VALUE_9 + 1
                ):
                if -1 != self._edit_setValue(key - self.KEY_VALUE_1 + 1)  : self.parent_.countChanged()
                #if key == (self.KEY_VALUE_1 + 6):
                #    self.sudoku_.elements_[index].hyp_ = 1

            case self.KEY_ENTER | self.KEY_NUM_ENTER:
                self._edit_stop()
                return
            case self.EDIT_CANCEL:
                self._edit_cancel()
                return
            case _:
                pass

        self._edit_selChanged()

    # Undo
    #
    def _edit_undo(self)->int:
        id:int = super()._edit_undo()
        if id > -1:
            self.draw()
        return id

    # Cancel
    #
    @override
    def _edit_cancel(self)->bool:
        done:bool = False
        if super()._edit_cancel():
            self.state_.remove(self.ARRAY_MODIFIED) # !!!
            self.sudoku_.hyp_rejectAll()
            self.draw()
            done = True

        self._edit_stop()
        return done

    # Update array during edition
    #
    @override
    def _edit_updatePos(self, prevPos:pointer | None, currentPos:pointer):
        super()._edit_updatePos(prevPos, currentPos)

        if self.helpVisible_:
            self._draw_helpMatrix_ex()

    #
    # Hyptohesis and tags
    #

    # The user click on a colour in the combo
    #
    #  colID : index (in the theme list) of the selected colour
    #
    #  @return : new hyps list if colour is valid None otherwise
    #
    def hyp_onComboSelect(self, colID:int)->list[element.hypColour] | None:
        if colID > 0 and colID not in self.hyps_:
            self.hyps_.append(element.hypColour(colID))

            self.SetFocusIgnoringChildren()     # canvas keep keyboard focus
            return self.hyps_

        return None

    # Accept the current hyp. => all tagged values will get prev. hyp. tag if exists or no tag (final validation)
    def _hyp_validate(self):
        id:int = len(self.hyps_)
        if id > 1:
            self.sudoku_.hyp_accept(self.hyps_[id-1], self.hyps_[id-2])
            id-=1

            self.parent_.hyp_onValidate(self.hyps_)
            self.draw_update()

    # Reject current hyp. => all values tagged will loose their tag
    def _hyp_reject(self):
        id:int = len(self.hyps_)
        if id > 1:
            self.sudoku_.hyp_reject(self.hyps_[id-1])   # notifies combo
            id-=1

            self.parent_.hyp_onReject(self.hyps_)   # notifies combo
            self.draw_update()

    #
    #  Menus
    #

    # Create the menubar and accelerators
    #
    def _menu_create(self):
        # Files
        fileMenu = wx.Menu()

        fileMenu.Append(wx.ID_OPEN)
        fileMenu.Append(wx.ID_SAVE)

        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        # Display
        displayMenu = wx.Menu()

        displayMenu.AppendCheckItem(menuConsts.ID_DISPLAY_CENTER, menuConsts.IDS_DISPLAY_CENTER)
        displayMenu.Check(menuConsts.ID_DISPLAY_CENTER, self.params_.center)

        displayMenu.AppendCheckItem(menuConsts.ID_DISPLAY_HELP, menuConsts.IDS_DISPLAY_HELP)
        displayMenu.Check(menuConsts.ID_DISPLAY_HELP, self.helpVisible_)

        # Themes management
        displayMenu.AppendSeparator()
        themesMenu = wx.Menu()
        for name in list(GUITheme.colourThemes.keys()):
            newID:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            self.menuThemesID_[name] = newID
            themesMenu.Append(newID, name)  # pyright: ignore[reportUnknownArgumentType]

        displayMenu.Append(wx.ID_ANY, menuConsts.IDS_DISPLAY_THEMES, themesMenu)

        # Creation
        createMenu = wx.Menu()
        createMenu.Append(menuConsts.ID_CREATE_EMPTY, menuConsts.IDS_CREATE_EMPTY)
        createMenu.Append(menuConsts.ID_CREATE_EASY, menuConsts.IDS_CREATE_EASY)
        createMenu.Append(menuConsts.ID_CREATE_MEDIUM, menuConsts.IDS_CREATE_MEDIUM)
        createMenu.Append(menuConsts.ID_CREATE_HARD, menuConsts.IDS_CREATE_HARD)
        createMenu.AppendSeparator()
        createMenu.Append(menuConsts.ID_EDIT_UNDO, menuConsts.IDS_CREATE_UNDO)
        createMenu.AppendSeparator()
        createMenu.Append(menuConsts.ID_EDIT_MODIFY, menuConsts.IDS_CREATE_MODIFY)
        createMenu.Append(menuConsts.ID_EDIT_DONE, menuConsts.IDS_CREATE_DONE)
        createMenu.Append(menuConsts.ID_EDIT_CANCEL, menuConsts.IDS_CREATE_CANCEL)

        # Resolution
        solveMenu = wx.Menu()
        solveMenu.Append(menuConsts.ID_SOLVE_MANUAL, menuConsts.IDS_SOLVE_MANUAL)
        solveMenu.Append(menuConsts.ID_SOLVE_OBVIOUS, menuConsts.IDS_SOLVE_OBVIOUS)

        resolveMenu = wx.Menu()
        resolveMenu.Append(menuConsts.ID_SOLVE_RESOLVE_SINGLE, menuConsts.IDS_SOLVE_RESOLVE_SINGLE)
        resolveMenu.Append(menuConsts.ID_SOLVE_RESOLVE_MULTI, menuConsts.IDS_SOLVE_RESOLVE_MULTI)
        solveMenu.Append(menuConsts.ID_SOLVE, menuConsts.IDS_SOLVE_RESOLVE, resolveMenu)

        solveMenu.Append(menuConsts.ID_SOLVE_REVERT, menuConsts.IDS_SOLVE_REVERT)

        # Menu bar creation
        self.menuBar_ : wx.MenuBar = wx.MenuBar()
        self.parent_.SetMenuBar(self.menuBar_)
        self.menuBar_.Append(fileMenu, menuConsts.IDS_FILE)
        self.menuBar_.Append(displayMenu, menuConsts.IDS_DISPLAY)
        self.menuBar_.Append(createMenu,menuConsts.IDS_CREATE)
        self.menuBar_.Append(solveMenu, menuConsts.IDS_SOLVE)

        self.parent_.SetMenuBar(self.menuBar_)
        self._menu_setItemsStates()     # initial states for items

        # Accelerators
        #
        entries:list[wx.AcceleratorEntry] = []

        # Create
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('0'), menuConsts.ID_CREATE_EMPTY))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_NUMPAD0, menuConsts.ID_CREATE_EMPTY))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('1'), menuConsts.ID_CREATE_EASY))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_NUMPAD1, menuConsts.ID_CREATE_EASY))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('2'), menuConsts.ID_CREATE_MEDIUM))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_NUMPAD2, menuConsts.ID_CREATE_MEDIUM))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('3'), menuConsts.ID_CREATE_HARD))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_NUMPAD3, menuConsts.ID_CREATE_HARD))

        # Edit
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('Z'), menuConsts.ID_EDIT_UNDO))
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('M'), menuConsts.ID_EDIT_MODIFY))

        # Solve
        entries.append(wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('R'), menuConsts.ID_SOLVE_REVERT))

        accel = wx.AcceleratorTable(entries)
        self.SetAcceleratorTable(accel)

    # Start edition or resolution
    #
    def _menu_editOrResolve(self, edit: bool, row: int | None = None, line: int | None = None):
        if edit:
            self.edition_.creating = True
            self.parent_.modeChanged(wxEditionMode.MODE_CREATION)
        else:
            self.edition_.manualSolving = True
            self.parent_.modeChanged(wxEditionMode.MODE_RESOLUTION)

        if row is not None and line is not None:    # selected item has just been clicked (or not)
            self.edition_.currentPos_.moveTo(line,row)
            self.edition_.prevPos_ = None

        self._edit_start(row is None)

    # Create a new or empty array
    #
    def _menu_fileNew(self, menuId:int):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.MessageBox(appStrings.STR_NOT_SAVED, appStrings.STR_NEW,
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        match menuId:
            case menuConsts.ID_CREATE_EASY:
                self.sudoku_.new(arrayComplexity.Easy)
            case menuConsts.ID_CREATE_MEDIUM:
                self.sudoku_.new(arrayComplexity.Medium)
            case menuConsts.ID_CREATE_HARD:
                self.sudoku_.new(arrayComplexity.Hard)
            case _:
                self.sudoku_.new(arrayComplexity.Empty)

        self.state_.assign(self.ARRAY_NEW)
        self._menu_setItemsStates()

        self.parent_.countChanged() # new elements have values
        self.draw_update()

    # Load an array
    #
    def _menu_fileOpen(self):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.MessageBox(appStrings.STR_NOT_SAVED, appStrings.STR_LOAD,
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        with wx.FileDialog(self, appStrings.STR_LOAD, wildcard=appStrings.STR_WILDCARD,
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnknownMemberType]

            if fileDialog.ShowModal() == wx.ID_CANCEL:  # pyright: ignore[reportUnknownMemberType]
                return     # the user changed its mind

        # New file just loaded
        self.fromFile(fileDialog.GetPath())  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        self.state_.assign(self.ARRAY_NEW)
        self._menu_setItemsStates()
        self.parent_.countChanged() # new elements have values

    # Save current array
    #
    def _menu_fileSave(self):
        if self.sudoku_.isEmpty():
            wx.MessageBox("The current sudoku array is empty.", appStrings.STR_SAVE,
                        wx.ICON_EXCLAMATION | wx.OK, self)
            return

        path : str | None = self.filename
        done : bool = False
        wildcard = appStrings.STR_WILDCARD

        with wx.FileDialog(
            self,
            message=appStrings.STR_SAVE,
            defaultFile=path,
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        ) as dlg:  # pyright: ignore[reportUnknownVariableType]
            if dlg.ShowModal() == wx.ID_OK:  # pyright: ignore[reportUnknownMemberType]
                path = dlg.GetPath()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

                # Save the sudoku
                path = self.sudoku_.save(newFileName=path, addExtent = FILE_EXTENSION)  # pyright: ignore[reportUnknownArgumentType]
                done = path is not None and len(path)>0  # pyright: ignore[reportArgumentType]

        if done :
            self.setFilename(path)
            self.state_.assign(self.ARRAY_NEW)
            self._menu_setItemsStates()

            wx.MessageBox(f"Current sudoku successfully saved as '{self.filename}'",
                        appStrings.STR_SAVE, wx.ICON_INFORMATION | wx.OK, self)

    # Quit
    #
    def _menu_fileExit(self):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.NO == wx.MessageBox(
                    appStrings.STR_NOT_SAVED, appStrings.STR_EXIT,
                    wx.ICON_QUESTION | wx.YES_NO, self):
            return

        self.Close(True)

    # Check/handle menu event from contextual menu
    #
    #   return True if item has been handled
    def _menu_handleContextualItems(self, menuId:int)->bool:
        done:bool = False

        # Check values
        for index in range(VALUE_MAX):
            if menuConsts.ID_POPUP_VALUES[index] == menuId:
                self._edit_setValue(index+1)
                done = True
                break

        # Empty ?
        if menuConsts.ID_POPUP_VALUES[VALUE_MAX] == menuId:
                self._edit_removeValue()
                done = True

        if done:
            self.parent_.countChanged()

        # Not found
        return done

    #
    # Resolving
    #

    def _menu_findOviousValues(self):
        if self.sudoku_.isOk():
            if self.findObviousValues():
                self.parent_.countChanged() # new elements have values
                self.draw_update()
                self._notify_start()
                wx.MessageBox(f"Found {self.stats_.obvValues_} obvious values in {round(self.stats_.obvDuration_,2)} sec.",
                    APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)
            else:
                wx.MessageBox("No obvious value found.", APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

    def _menu_resolveSingleThread(self):
        if self.sudoku_.isOk():
            self.params_.progressMode_ = self.params_.PROGRESS_SHOW_SAME_THREAD

            if self.resolve():
                self.draw_update()
                self._resolve_showStats()
            else:
                wx.MessageBox(appStrings.STR_NO_SOLUTION, APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

    def _menu_resolve_multiThreaded(self):
        if self.sudoku_.isOk():
            self.directDraw_ = True
            self.params_.progressMode_ = self.params_.PROGRESS_MULTITHREADED

            if not self.resolve():
                wx.MessageBox(appStrings.STR_NO_SOLUTION, APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

            self.directDraw_ = False
            self.draw_update()
            self._resolve_showStats()

    # Return to original array's state (remove added values)
    #
    def _menu_revertArray(self):
        if self.sudoku_.isOk():
            self.sudoku_.revert()
            self.draw_update()

    # Change items ' states
    #
    def _menu_setItemsStates(self):
        #modified : bool = self.state_.isSet(self.ARRAY_MODIFIED)
        valid : bool = self.sudoku_.isOk()
        editOn : bool = self.state_.isSet(self.ARRAY_EDITING)
        solving : bool = self.state_.isSet(self.ARRAY_SOLVING)

        self.menuBar_.Enable(menuConsts.ID_EDIT_UNDO, editOn)
        self.menuBar_.Enable(menuConsts.ID_EDIT_DONE, editOn)
        self.menuBar_.Enable(menuConsts.ID_EDIT_CANCEL, editOn)

        state : bool = not (editOn or solving)

        self.menuBar_.Enable(menuConsts.ID_CREATE_EMPTY, state)
        self.menuBar_.Enable(menuConsts.ID_CREATE_EASY, state)
        self.menuBar_.Enable(menuConsts.ID_CREATE_MEDIUM, state)
        self.menuBar_.Enable(menuConsts.ID_CREATE_HARD, state)
        self.menuBar_.Enable(wx.ID_OPEN, state)
        self.menuBar_.Enable(wx.ID_SAVE, state)

        state = state and valid

        self.menuBar_.Enable(menuConsts.ID_EDIT_MODIFY, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_MANUAL, state)

        self.menuBar_.Enable(menuConsts.ID_SOLVE, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_OBVIOUS, state)
        #self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_SINGLE, state)
        #self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_MULTI, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_REVERT, state)

    # Mouse position : client -> array coordinates
    #
    # @return : (ZoneID, x coordinate, y coordinate)
    #           If ZoneID == ZONE_NOWHERE, x and y are undefined
    #@override
    def _mouse_translatePosition(self, pos: tuple[int,int])->tuple[solver.ownZone, int, int]:
        ret:tuple[int, int, int] = solver.solver._mouse_translatePosition(self, pos)
        if ret[0] == solver.ownZone.ZONE_NOWHERE and self.helpVisible_:
            # not in the array -> in the matrix ?
            elementWidth = self.helpIntSquareWidth_ + 2 * GUIConsts.EXT_BORDER_THICK
            matrixWidth:int = 3 * elementWidth

            if pos[0] >= self.helpOffsets_[0] and pos[1] >= self.helpOffsets_[1] and pos[0] < (self.helpOffsets_[0] + matrixWidth) and pos[1] < (self.helpOffsets_[1] + matrixWidth):
                return (solver.ownZone.ZONE_HELP_MATRIX, math.floor((pos[0] - self.helpOffsets_[0]) / elementWidth),
                    math.floor((pos[1] - self.helpOffsets_[1]) / elementWidth))

        return ret

    #
    #  Element(s)' notifications
    #
    @override
    def _notify_start(self, freq:int = GUIConsts.TIMER_RATE_SELECTED, max:int = GUIConsts.BLINK_COUNT_MODIFYING):
        super()._notify_start()
        self.notify_ = False
        self.notifyCount_ = max
        if not self.notifyTimer_.IsRunning():
            self.notifyTimer_.Start(freq)

    def _notify_drawElements(self):
        super()._notify_drawElements()

        self.notifyCount_-=1
        if 1 == self.notifyCount_:
            self._notify_stop()

        self._draw_startUp()
        position: pointer = pointer(game = False)
        for line in range(LINE_COUNT):
            for row in range(ROW_COUNT):
                currentElement = self.sudoku_[position.index()]
                if currentElement.notifying:
                    bk, txt = self._theme_getElementColours(position.index(), False)
                    self._draw_singleElement(
                        row, line,
                        currentElement.num if self.notify_ else 0,
                        bk, txt,
                        currentElement.hypothesis,
                    )

                # next element ...
                position+=1
        self._draw_end()

        self.notify_ = not self.notify_

    @override
    def _notify_stop(self, endApp:bool = False):
        super()._notify_stop(endApp)
        if self.notifyTimer_.IsRunning():
            self.notifyTimer_.Stop()

    # Show resolution stats
    #
    @override
    def _resolve_showStats(self):
        wx.MessageBox(f"Found a solution:\n\t in {round(self.stats_.bruteDuration_,2)} sec.\n\t with {self.stats_.bruteAttempts_} attempt(s)",
            APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)
    #
    # Themes
    #

    # Change colour's theme
    #
    @override
    def _theme_changeByName(self, name:str)->bool:
        ret: bool = solver.solver._theme_changeByName(self, name)
        if ret:
            self._draw_freeMemoryDC()
            self._theme_fontChanged()
            self.draw(redrawBackground=True)
            self.parent_.themeChanged()
        return ret

    # Convert colour objects from ownColour to wx.Colour
    #
    @override
    def _theme_convertColours(self):
        for id in range(len(self.theme_)):
            basicColour:GUITheme.ownColour =self.theme_[id]
            self.theme_[id].other = wx.Colour(
                basicColour.r,
                basicColour.g,
                basicColour.b,
                basicColour.a)

    # set a new font (new name or new size)
    def _theme_fontChanged(self):
        if self.memDC_ is not None and self.memDC_.IsOk():
            self._draw_fontSize2PixelSize()

            # small font size
            self.helpCanvasFontSize_ = math.floor(self.canvasFontSize_ / GUIConsts.HELP_RATIO)

            self.memDC_.SetFont(NullFont)
            self.elementFont_ = wx.Font(pointSize=self.canvasFontSize_,
                            family=wx.FONTFAMILY_DEFAULT,
                            style=wx.FONTSTYLE_ITALIC if self.theme_.canvasFont_.italic else wx.FONTSTYLE_NORMAL,
                            weight=self.theme_.canvasFont_.weight,
                            faceName = self.theme_.canvasFont_.faceName)
            self.memDC_.SetFont(self.elementFont_)

            # create a smaller font for element's value help
            self.helpFont_ = wx.Font(pointSize=self.helpCanvasFontSize_,
                            family=wx.FONTFAMILY_DEFAULT,
                            style=wx.FONTSTYLE_ITALIC if self.theme_.canvasFont_.italic else wx.FONTSTYLE_NORMAL,
                            weight=self.theme_.canvasFont_.weight,
                            faceName = self.theme_.canvasFont_.faceName)

            dims : wx.Size
            self.textOffsets_.clear()       # (re)compute offsets to center texts in array and help matrix
            for index in range(VALUE_MAX):
                dims = self.memDC_.GetTextExtent(f"{index+1}")
                realOffset = wx.Size(math.floor((self.intSquareWidth_ - dims.width) / 2), math.floor((self.intSquareWidth_ - dims.height) / 2))
                smallOffset = wx.Size(math.floor(realOffset.x/GUIConsts.HELP_RATIO), math.floor(realOffset.y/GUIConsts.HELP_RATIO))
                self.textOffsets_.append((realOffset, smallOffset))

#
#  Owner-drawn combobox
#

# Own datas stored with combo's tiems
#
class wxOwnComboData:
    def __init__(self, id:int, colour:GUITheme.ownColour):
        self.id_:int = id   # Id of the hyp. colour
        self.colour_:wx.Colour = colour.other

# Owner-drawn combobox for hypothesis management
#
class wxOwnCombo(wx.adv.OwnerDrawnComboBox):
    # Construction
    def __init__(self, parent:wx.ToolBar, canvas: wxSolverCanvas):
        super().__init__(parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.Size(120, -1),style=wx.CB_READONLY )

        #self.parent_:wxOwnPanel = parent
        self.canvas_:wxSolverCanvas = canvas
        self.hyps_:list[wxOwnComboData] = []    # no colours at startup !

    # Set or change colour list
    def setColours(self)->int:
        sel:int = self.GetSelection()  # pyright: ignore[reportAssignmentType]
        self.Clear()
        self.hyps_.clear()

        data = wxOwnComboData(id=0, colour=GUITheme.ownColour(rgb=(255,255,255)))   # No hyp / No Colour
        self.hyps_.append(data)
        self.Append(f"{data.id_}", data)  # pyright: ignore[reportUnknownMemberType]

        for index in range(4):
            data = wxOwnComboData(index+1, self.canvas_.theme_[index + GUITheme.colourID.ID_TAG_1])

            self.hyps_.append(data)
            self.Append(f"{data.id_}", data)  # pyright: ignore[reportUnknownMemberType]

        if sel!= wx.NOT_FOUND and sel <= self.GetCount():
            self.SetSelection(sel)  # pyright: ignore[reportCallIssue]

        return self.GetSelection()  # pyright: ignore[reportReturnType]

    # Update the combo to reflect user's hyp.
    def updateColours(self, colours: list[element.hypColour])->int:
        self.setColours()

        count:int = len(colours)
        if count <= 1:  # should never be equal to 0 !!!!
            return self.GetSelection()  # pyright: ignore[reportReturnType]

        index:int = 0
        position:int
        while index < self.GetCount():
            data:wxOwnComboData = self.GetClientData(index)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

            try:
                position = colours.index(data.id_)  # pyright: ignore[reportArgumentType, reportUnknownMemberType]
            except ValueError:
                position = -1
                index+=1

            if position != -1 :
                if position != (count-1):
                    self.Delete(index)
                else:
                    self.SetSelection(index)  # pyright: ignore[reportCallIssue]
                    index+=1

        return self.GetSelection()  # pyright: ignore[reportReturnType]

    # Draw a single element in the drop list
    def OnDrawItem(self, dc: wx.DC, rect: wx.Rect, item:int, flags:int):
        if item == wx.NOT_FOUND:
            return

        data:wxOwnComboData = self.GetClientData(item)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
        if data is not None and isinstance(data, wxOwnComboData):
            r = rect
            boxSize = r.height - 2 * GUIConsts.TAG_COMBO_BORDER
            col:wx.Colour = data.colour_

            if data.id_ != 0:
                # Draw a small colored rectangle
                dc.SetBrush(wx.Brush(colour=col))
                dc.SetPen(wx.Pen(col, 1))
                dc.DrawRectangle(r.x + GUIConsts.TAG_COMBO_BORDER, r.y + GUIConsts.TAG_COMBO_BORDER, r.width - 2 * GUIConsts.TAG_COMBO_BORDER, boxSize)
            else:
                # if not a color draw text ...
                dc.SetFont(self.GetFont())
                textPosX = r.x + boxSize + GUIConsts.TAG_COMBO_BORDER
                if flags & wx.adv.ODCB_PAINTING_CONTROL:
                    dc.SetTextForeground(self.GetForegroundColour())
                elif flags & wx.adv.ODCB_PAINTING_SELECTED:
                    dc.SetTextForeground(wx.WHITE)
                else:
                    dc.SetTextForeground(col)
                dc.DrawLabel(GUIConsts.TAG_COMBO_NO_COLOUR_STR,
                                wx.Rect(textPosX, r.y, r.width - textPosX, r.height),
                                wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

    def OnDrawBackground(self, dc:wx.DC, rect:wx.Rect, item:int, flags:int):
        if flags & wx.adv.ODCB_PAINTING_SELECTED and not (flags & wx.adv.ODCB_PAINTING_CONTROL):
            dc.SetBrush(wx.Brush(wx.Colour(GUIConsts.TAG_COMBO_SEL_COLOUR)))
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.DrawRectangle(rect)
        else:
            super().OnDrawBackground(dc, rect, item, flags)

    # Item's height
    def OnMeasureItem(self, item:int):
        return GUIConsts.TAG_COMBO_HEIGHT

    # Item's height
    def OnMeasureItemWidth(self, item:int):
        return -1  # use default width

# wxSolverFrame - App. main frame
#
class wxSolverFrame(wxMainFrame):
    def __init__(self, params: options):
        wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = wx.DEFAULT_FRAME_STYLE, size=wx.Size(450, 300))

        # sudoku solver canvas
        self.canvas_ = wxSolverCanvas(self, params)

        # Create the toolbar
        #
        self.toolBar_:wx.ToolBar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.TB_TEXT)  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        self.toolBar_.SetToolBitmapSize(wx.Size(16, 16))  # default bitmaps size

        self.labelMode_ = wx.StaticText(self.toolBar_, label=appStrings.STR_TOOLBAR)
        self.toolBar_.AddControl(self.labelMode_)
        #self.toolBar_.AddSeparator()
        self.labelCount_ = wx.StaticText(self.toolBar_, label="Filled")
        self.toolBar_.AddControl(self.labelCount_)
        self.toolBar_.AddSeparator()

        # Hypothesis and flags
        """
        self.combo_ = wx.ComboBox(self.toolBar_, wx.ID_ANY, choices=["Projet A", "Projet B", "Projet C"],
                                 style=wx.CB_DROPDOWN | wx.CB_READONLY, size=wx.Size(170, -1))
        """
        self.combo_ = wxOwnCombo(self.toolBar_, self.canvas_)
        self.comboSel_:int = 0
        self.toolBar_.AddControl(self.combo_, menuConsts.IDS_TIP_HYP_COMBO)

        self.toolBar_.AddTool(menuConsts.ID_HYP_VALIDATE, menuConsts.IDS_HYP_VALIDATE, wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR),  # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
                   menuConsts.IDS_TIP_HYP_VALIDATE)
        self.toolBar_.AddTool(menuConsts.ID_HYP_REJECT, menuConsts.IDS_HYP_REJECT, wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR),  # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
                   menuConsts.IDS_TIP_HYP_REJECT)
        self.toolBar_.AddSeparator()

        # End edition / creation
        self.toolBar_.AddTool(menuConsts.ID_EDIT_END, menuConsts.IDS_EDIT_END, wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_TOOLBAR),    # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
                   menuConsts.IDS_TIP_EDIT_END)
        self.toolBar_.AddTool(menuConsts.ID_EDIT_CANCEL, menuConsts.IDS_EDIT_CANCEL, wx.ArtProvider.GetBitmap(wx.ART_DEL_BOOKMARK, wx.ART_TOOLBAR),    # pyright: ignore[reportCallIssue, reportUnknownMemberType, reportArgumentType]
                   menuConsts.IDS_TIP_EDIT_CANCEL)

        self.toolBar_.Realize()  # indispensable pour afficher la barre

        # Add the canvas to the frame's sizer
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(self.canvas_, 1, wx.EXPAND)       # pyright: ignore[reportUnknownMemberType]
        self.SetSizer(mainSizer)

        # Bind events to handlers
        self.Bind(wx.EVT_MENU, self.OnMenu)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_COMBOBOX, self.hyp_onComboSelect, self.combo_)  # pyright: ignore[reportUnknownMemberType]

    # GUI initialization
    #
    def initialize(self):
        #self.sidebar_show(force=True, visible=False)  # not visible at startup
        self.canvas_.initialize()

        self.combo_.setColours()
        self.combo_.SetSelection(0)  # pyright: ignore[reportCallIssue]
        self.comboSel_ = 0

        # updates ...
        self.themeChanged()
        self.countChanged()
        self.modeChanged(wxEditionMode.MODE_NONE)

        # Let's go !!!
        self.Centre()
        self.Show()

    # Theme just changed
    @override
    def themeChanged(self):
        self.SetBackgroundColour(self.canvas_.theme_[GUITheme.colourID.ID_TB_BK].other)
        self.labelMode_.SetForegroundColour(self.canvas_.theme_[GUITheme.colourID.ID_TB_TXT].other)
        self.labelCount_.SetForegroundColour(self.canvas_.theme_[GUITheme.colourID.ID_TB_TXT].other)
        font = wx.Font(pointSize=self.canvas_.theme_.textFont_.size,
                        family=wx.FONTFAMILY_DEFAULT,
                        style=wx.FONTSTYLE_ITALIC if self.canvas_.theme_.textFont_.italic else wx.FONTSTYLE_NORMAL,
                        weight=self.canvas_.theme_.textFont_.weight,
                        faceName = self.canvas_.theme_.textFont_.faceName)
        self.labelMode_.SetFont(font)
        self.labelCount_.SetFont(font)

    # count of elements changed
    @override
    def countChanged(self):
        if self.canvas_.sudoku_.isOk():
            self.labelCount_.SetLabel(f"{appStrings.STR_FILLED}{self.canvas_.sudoku_.nonEmpty} / {ARRAY_SIZE}")
        else:
            self.labelCount_.SetLabel(f"{appStrings.STR_FILLED}_ / _")

    # edition mode changed
    @override
    def modeChanged(self, mode:wxEditionMode):
        self.labelMode_.SetLabel(f"{appStrings.STR_TOOLBAR}" if mode == wxEditionMode.MODE_NONE
            else f"{appStrings.STR_MODE_CREATION if mode == wxEditionMode.MODE_CREATION else appStrings.STR_MODE_RESOLUTION}")

        create:bool = (mode == wxEditionMode.MODE_CREATION)
        solve:bool = (mode == wxEditionMode.MODE_RESOLUTION)

        self.combo_.Enable(solve)
        self.toolBar_.EnableTool(menuConsts.ID_HYP_VALIDATE, solve)
        self.toolBar_.EnableTool(menuConsts.ID_HYP_REJECT, solve)

        self.toolBar_.EnableTool(menuConsts.ID_EDIT_END, solve | create)
        self.toolBar_.EnableTool(menuConsts.ID_EDIT_CANCEL, solve | create)

    # Hypothesis / tag management
    #

    @override
    def hyp_onReject(self, colours: list[element.hypColour]):
        self.combo_.updateColours(colours)

    @override
    def hyp_onValidate(self, colours: list[element.hypColour]):
        self.combo_.updateColours(colours)

    # Click on the combo list
    def hyp_onComboSelect(self, event: wx.Event):
        index:int = self.combo_.GetSelection()  # pyright: ignore[reportAssignmentType]

        if index != wx.NOT_FOUND:
            data:wxOwnComboData | None = self.combo_.GetClientData(index)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            if data is not None and isinstance(data, wxOwnComboData) and data.id_ != 0 :  # pyright: ignore[reportUnknownMemberType]
                ret: list[element.hypColour] | None = self.canvas_.hyp_onComboSelect(data.id_)  # pyright: ignore[reportUnknownArgumentType]
                if ret is not None:
                    self.combo_.updateColours(ret)
                    #print(f"colours : {ret}")  # pyright: ignore[reportUnknownMemberType]

    # End drawings
    #
    def end(self):
        self.canvas_.end()

    # Click on a menu item
    #
    def OnMenu(self, event:wx.MenuEvent):
        menuId = event.GetId()

        match menuId:
            case wx.ID_EXIT:
                self.Destroy()
            case _:
                self.canvas_.OnMenu(event)  # Other events are handled by the canvas panel

# EOF
