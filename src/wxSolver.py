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
from typing import override

try :
    import wx  # pyright: ignore[reportMissingTypeStubs]
except ModuleNotFoundError:
    print("wxPython library is not installed")
    sys.exit(0)

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


# wxMainFrame
#   abstract class
#
#   Allow interactions with contained toolbar/sidebar and canvas panel
#
class wxMainFrame(wx.Frame):

    # Theme just changed
    #
    def themeChanged(self):
        pass

    # Hypothesis / tag management
    #
    def hyp_onSelectColor(self, colID:int):
        pass
    def hyp_onReject(self, colID:int):
        pass
    def hyp_onAccept(self, colID:int):
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
    def setTheme(self):
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
    KEY_VALUE_INC:int = wx.WXK_PAGEUP

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
        self.memDC_ : wx.MemoryDC | None = None # all display are made in a memory DC
        self.directDraw_:bool = False
        self.clientSize_: wx.Size = wx.Size(0,0)
        self.textOffsets_: wx.Size = wx.Size(0,0)  # for text in array
        self.font_ = wx.Font(GUIConsts.ELT_FONT_SIZE,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL,
                        faceName = self.theme_.canvasFontName)

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
    def setFilename(self, fileName:str, create:bool = False):
        solver.solver.setFilename(self, fileName, create)

        title : str = APP_SHORT_NAME
        if len(fileName) > 0:
            title = title + " - " + fileName

        self.parent_.SetTitle(title)

    # Show resolution stats
    #
    @override
    def showStats(self):
        wx.MessageBox(f"Found a solution:\n\t in {round(self.stats_.bruteDuration_,2)} sec.\n\t with {self.stats_.bruteAttempts_} attempt(s)",
            APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

    #
    # Event handlers
    #

    # Click on a menu item
    #
    def OnMenu(self, event:wx.MenuEvent):
        menuId = event.GetId()
        #menu = event.GetEventObject()
        #print(f"Item : {menu.GetLabelText(menuId)}")

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

            case menuConsts.ID_EDIT_UNDO:
                self._edit_undo()
            case menuConsts.ID_EDIT_MODIFY:
                self.edition_.creating = True
                self._edit_start()
            case menuConsts.ID_EDIT_DONE:
                self._edit_stop()
                self.edition_.creating = False
            case menuConsts.ID_EDIT_CANCEL:
                self._edit_cancel()
                self.edition_.creating = False

            case menuConsts.ID_SOLVE_MANUAL:
                self.edition_.manualSolving = True
                self._edit_start()
            case menuConsts.ID_SOLVE_OBVIOUS:
                self._menu_findOviousValues()
            case menuConsts.ID_SOLVE_RESOLVE_SINGLE:
                    self._menu_resolveSingleThread()
            case menuConsts.ID_SOLVE_RESOLVE_MULTI:
                    self._menu_resolve_multiThreaded()
            case menuConsts.ID_SOLVE_REVERT:
                    self._menu_revertArray()

            case wx.ID_EXIT:
                self._menu_fileExit()
            case _:
                pass

        # Change theme ?
        if menuId in self.menuThemesID_.values():
           keys:list[str] = [k for k, v in self.menuThemesID_.items() if v == menuId]
           if self._draw_changeTheme(keys[0], menuId):
               self._draw_freeMemoryDC()
               self.draw(redrawBackground=True)
               self.parent_.themeChanged()

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
            self.edition_.move()
            newPos: tuple[int,int] = self._mouse_translatePosition(pos=(event.x, event.y))

            if newPos[0]!=-1 and self.edition_.currentPos_.moveTo(pos=newPos):
                self._edit_selChanged()

            return

        event.Skip()  # Allow other handlers to process the key

    # User clicked  with right button => display contextual menu
    #
    def OnRButtonUp(self, event : wx.MouseEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            self.edition_.move()
            newPos : tuple[int,int] = self._mouse_translatePosition(pos=(event.x, event.y))

            if self.edition_.currentPos_.moveTo(pos=newPos):
                self._edit_selChanged()

            # possible values
            values: list[int] =self.sudoku_.getValues(self.edition_.currentPos_)

            # Generate a contextual menu at mouse pos with all possible values
            popUp: wx.Menu = wx.Menu()
            popUp.Append(menuConsts.ID_POPUP_VALUES[9], menuConsts.IDM_POPUP_EMPTY)
            popUp.Enable(menuConsts.ID_POPUP_VALUES[9], not self.sudoku_.elements_[self.edition_.currentPos_.index_].isEmpty())
            for index in range(1,10):
                id = menuConsts.ID_POPUP_VALUES[index-1]
                popUp.Append(id, f"{index}")
                if index not in values :
                    popUp.Enable(id, False)

            self.PopupMenu(popUp, event.GetPosition())
            popUp.Destroy()

            return

        event.Skip()  # Allow other handlers to process the key

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
        self.font_.SetPixelSize(wx.Size(0, self.canvasFontSize_))

        self._draw_freeMemoryDC()

        # Create memory DC with bitmap
        self._draw_startUp()

        # Numbers are centered !
        if self.memDC_ is not None and self.memDC_.IsOk() :
            self.memDC_.SetFont(self.font_)
            dims : wx.Size = self.memDC_.GetTextExtent("O")
            self.textOffsets_ = wx.Size(math.floor((self.extSquareWidth_ - dims.width) / 2), math.floor((self.extSquareWidth_ - dims.height) / 2))

        # Redraw the whole array
        self._draw_background()
        self.draw()

    # Timer notification
    #
    def OnTimer(self, event : wx.Event):
        match event.Id:
            case GUIConsts.TIMER_ID_SELECTED:
                self._edit_selectionBlink()

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
            self.memDC_.SetFont(self.font_)
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

            # thin borders ...
            #
            pen = wx.Pen(self.theme_[GUITheme.colourID.ID_FRAME_BORDER].other, 1, wx.PENSTYLE_SOLID)
            self.memDC_.SetPen(pen)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = row * self.extSquareWidth_ + self.offsets_[0]
                    y = line * self.extSquareWidth_ + self.offsets_[1]
                    self.memDC_.DrawLine(x, y, x, y + self.extSquareWidth_)
                    self.memDC_.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            # ... large ext. borders
            #
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

        # Erase background
        self.memDC_.SetBrush(wx.Brush(self.theme_[bkColourID].other))
        self.memDC_.SetPen(wx.TRANSPARENT_PEN)
        self.memDC_.DrawRectangle(x, y, self.intSquareWidth_, self.intSquareWidth_)

        # The value (if valid)
        if value is not None and value > 0:
            self.memDC_.SetTextForeground(self.theme_[txtColourID].other)
            self.memDC_.DrawText(str(value), x + self.textOffsets_.x, y + self.textOffsets_.y)

            # Hypothesis/Tag ?
            if hypColourID != element.hypColour.NO_COLOUR:
                self.memDC_.SetBrush(wx.Brush(self.theme_[hypColourID + GUITheme.colourID.ID_TAG_1 - 1].other))
                self.memDC_.SetPen(wx.TRANSPARENT_PEN)

                radius = int(self.tagWidth_ / 2)

                if self.tagWidth_ == GUIConsts.TAG_MIN_SIZE:
                    self.memDC_.DrawCircle(
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

                    self.memDC_.DrawPolygon(  # pyright: ignore[reportUnknownMemberType]
                        points,
                        x + self.intSquareWidth_ - GUIConsts.TAG_PADDING - self.tagWidth_,
                        y + GUIConsts.TAG_PADDING)


    # Convert colour objects from ownColour to wx.Colour
    #
    @override
    def _draw_convertColours(self):
        for id in range(len(self.theme_)):
            basicColour:GUITheme.ownColour =self.theme_[id]
            self.theme_[id].other = wx.Colour(
                basicColour.r,
                basicColour.g,
                basicColour.b,
                basicColour.a)

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
            if wx.MessageBox(GUIConsts.STR_MODIFIED_ARRAY, GUIConsts.STR_CREATE,
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

            if self.sudoku_.setOriginal():
                self.draw_update()

        super()._edit_start(initPos)
        self._notify_stop() # Don't forget to stop notification timer !

        self.state_.set(self.ARRAY_EDITING)
        self._menu_setItemsStates()

        # Anything to edit ?
        if len(self.sudoku_.elements_) == 0:
            self.sudoku_.empty()

        if initPos:
            self.edition_.clear()    # move to cursor to (0,0)
        else:
            self.edition_.selected = False

        self._edit_selectionBlink()
        if not self.selectedTimer_.IsRunning():
            self.selectedTimer_.Start(GUIConsts.TIMER_RATE_SELECTED)

    # End of edition mode
    #
    @override
    def _edit_stop(self, endApp:bool = False):
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
            self._draw_end()

    # Selected item has just changed
    #
    def _edit_selChanged(self):
        #self._edit_stop()
        self._edit_updatePos(self.edition_.prevPos_, self.edition_.currentPos_)
        #self._edit_start(False)

    def _edit_selectionBlink(self):
        self._draw_startUp()
        self._draw_selectedElement(self.edition_.changeSelectedStatus())
        self._draw_end()

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
            case key if key in range(
                self.KEY_VALUE_1, self.KEY_VALUE_9 + 1
            ):
                _ = self._edit_setValue(key - self.KEY_VALUE_1 + 1)
                #if key == (self.KEY_VALUE_1 + 6):
                #    self.sudoku_.elements_[index].hyp_ = 1
            case self.KEY_VALUE_DEC:
                self._edit_decValue()
            case self.KEY_VALUE_INC:
                self._edit_incValue()
            case self.KEY_REMOVE_VALUE:
                self._edit_removeValue()
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
            self.draw()
            done = True

        self._edit_stop()
        return done

    #
    #  Menus
    #

    # Create the menubar and accelerators
    #
    def _menu_create(self):
        # Files
        #
        fileMenu = wx.Menu()

        fileMenu.Append(wx.ID_OPEN)
        fileMenu.Append(wx.ID_SAVE)

        fileMenu.AppendSeparator()  # Themes management
        fileMenu.AppendCheckItem(menuConsts.ID_SIDEBAR, menuConsts.IDM_SIDEBAR)
        fileMenu.Check(menuConsts.ID_SIDEBAR, True)

        fileMenu.AppendSeparator()  # Themes management
        themesMenu = wx.Menu()
        for name in list(GUITheme.colourThemes.keys()):
            newID:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            self.menuThemesID_[name] = newID
            themesMenu.Append(newID, name)  # pyright: ignore[reportUnknownArgumentType]

        fileMenu.Append(wx.ID_ANY, menuConsts.IDM_THEMES, themesMenu)
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        # Creation
        #
        createMenu = wx.Menu()
        createMenu.Append(menuConsts.ID_CREATE_EMPTY, menuConsts.IDM_CREATE_EMPTY)
        createMenu.Append(menuConsts.ID_CREATE_EASY, menuConsts.IDM_CREATE_EASY)
        createMenu.Append(menuConsts.ID_CREATE_MEDIUM, menuConsts.IDM_CREATE_MEDIUM)
        createMenu.Append(menuConsts.ID_CREATE_HARD, menuConsts.IDM_CREATE_HARD)
        createMenu.AppendSeparator()
        createMenu.Append(menuConsts.ID_EDIT_UNDO, menuConsts.IDM_CREATE_UNDO)
        createMenu.AppendSeparator()
        createMenu.Append(menuConsts.ID_EDIT_MODIFY, menuConsts.IDM_CREATE_MODIFY)
        createMenu.Append(menuConsts.ID_EDIT_DONE, menuConsts.IDM_CREATE_DONE)
        createMenu.Append(menuConsts.ID_EDIT_CANCEL, menuConsts.IDM_CREATE_CANCEL)

        # Resolution
        solveMenu = wx.Menu()
        solveMenu.Append(menuConsts.ID_SOLVE_MANUAL, menuConsts.IDM_SOLVE_MANUAL)
        solveMenu.Append(menuConsts.ID_SOLVE_OBVIOUS, menuConsts.IDM_SOLVE_OBVIOUS)

        resolveMenu = wx.Menu()
        resolveMenu.Append(menuConsts.ID_SOLVE_RESOLVE_SINGLE, menuConsts.IDM_SOLVE_RESOLVE_SINGLE)
        resolveMenu.Append(menuConsts.ID_SOLVE_RESOLVE_MULTI, menuConsts.IDM_SOLVE_RESOLVE_MULTI)
        solveMenu.Append(wx.ID_ANY, menuConsts.IDM_SOLVE_RESOLVE, resolveMenu)

        solveMenu.Append(menuConsts.ID_SOLVE_REVERT, menuConsts.IDM_SOLVE_REVERT)

        # Menu bar creation
        self.menuBar_ : wx.MenuBar = wx.MenuBar()
        self.parent_.SetMenuBar(self.menuBar_)
        self.menuBar_.Append(fileMenu, menuConsts.IDM_FILE)
        self.menuBar_.Append(createMenu,menuConsts.IDM_CREATE)
        self.menuBar_.Append(solveMenu, menuConsts.IDM_SOLVE)

        self.parent_.SetMenuBar(self.menuBar_)
        self._menu_setItemsStates()     # initial states for items

        # Accelerators
        #
        entries:list[wx.AcceleratorEntry] = []

        # New
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

    # Change items ' states
    # '
    def _menu_setItemsStates(self):
        #modified : bool = self.state_.isSet(self.ARRAY_MODIFIED)
        valid : bool = self.sudoku_.IsOk()
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

        self.menuBar_.Enable(menuConsts.ID_EDIT_MODIFY, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_MANUAL, state)

        state = state and valid
        self.menuBar_.Enable(menuConsts.ID_SOLVE_OBVIOUS, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_SINGLE, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_MULTI, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_REVERT, state)

    # Create a new or empty array
    #
    def _menu_fileNew(self, menuId:int):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.MessageBox(GUIConsts.STR_NOT_SAVED, GUIConsts.STR_NEW,
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

        self.draw_update()

    # Load an array
    #
    def _menu_fileOpen(self):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.MessageBox(GUIConsts.STR_NOT_SAVED, GUIConsts.STR_LOAD,
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        with wx.FileDialog(self, GUIConsts.STR_LOAD, wildcard=GUIConsts.STR_WILDCARD,
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnknownMemberType]

            if fileDialog.ShowModal() == wx.ID_CANCEL:  # pyright: ignore[reportUnknownMemberType]
                return     # the user changed their mind

        # New file just loaded
        self.fromFile(fileDialog.GetPath())  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        self.state_.assign(self.ARRAY_NEW)
        self._menu_setItemsStates()

    # Save current array
    #
    def _menu_fileSave(self):
        if self.sudoku_.isEmpty():
            wx.MessageBox("The current sudoku array is empty.", GUIConsts.STR_SAVE,
                        wx.ICON_EXCLAMATION | wx.OK, self)
            return

        path : str | None = self.filename
        done : bool = False
        wildcard = GUIConsts.STR_WILDCARD

        with wx.FileDialog(
            self,
            message=GUIConsts.STR_SAVE,
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
            self.setFilename(path)  # pyright: ignore[reportUnknownArgumentType, reportArgumentType]
            self.state_.assign(self.ARRAY_NEW)
            self._menu_setItemsStates()

            wx.MessageBox(f"Current sudoku successfully saved as '{self.filename}'",
                        GUIConsts.STR_SAVE, wx.ICON_INFORMATION | wx.OK, self)


    # Quit
    #
    def _menu_fileExit(self):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.NO == wx.MessageBox(
                    GUIConsts.STR_NOT_SAVED, GUIConsts.STR_EXIT,
                    wx.ICON_QUESTION | wx.YES_NO, self):
            return

        self.Close(True)

    # Check/handle menu event from contextualmenu
    #
    #   return True if item has been handled
    def _menu_handleContextualItems(self, menuId:int)->bool:
        # Check values
        for index in range(VALUE_MAX):
            if menuConsts.ID_POPUP_VALUES[index] == menuId:
                self._edit_setValue(index+1)
                return True

        # Empty ?
        if menuConsts.ID_POPUP_VALUES[VALUE_MAX] == menuId:
                self._edit_removeValue()
                return True

        # Not found
        return False

    #
    # Resolving
    #

    def _menu_findOviousValues(self):
        if self.sudoku_.IsOk():
            if self.findObviousValues():
                self.draw_update()
                self._notify_start()
                wx.MessageBox(f"Found {self.stats_.obvValues_} obvious values in {round(self.stats_.obvDuration_,2)} sec.",
                    APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)
            else:
                wx.MessageBox("No obvious value found.", APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

    def _menu_resolveSingleThread(self):
        if self.sudoku_.IsOk():
            self.params_.progressMode_ = self.params_.PROGRESS_SHOW_SAME_THREAD

            if self.resolve():
                self.draw_update()
                self.showStats()
            else:
                wx.MessageBox(GUIConsts.STR_NO_SOLUTION, APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

    def _menu_resolve_multiThreaded(self):
        if self.sudoku_.IsOk():
            self.directDraw_ = True
            self.params_.progressMode_ = self.params_.PROGRESS_MULTITHREADED

            if not self.resolve():
                wx.MessageBox(GUIConsts.STR_NO_SOLUTION, APP_SHORT_NAME, wx.ICON_INFORMATION | wx.OK, self)

            self.directDraw_ = False
            self.draw_update()
            self.showStats()

    # Return to original array's state (remove added values)
    #
    def _menu_revertArray(self):
        if self.sudoku_.IsOk():
            self.sudoku_.revert()
            self.draw_update()

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
                currentElement = self.sudoku_.elements_[position.index()]
                if currentElement.notifying:
                    bk, txt = self._draw_getElementColours(position.index(), False)
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

# wxSidebarPanel - Sidebar
#
class wxSidebarPanel(wxOwnPanel):
    MODE_NONE:int = 0
    MODE_CREATION:int = 1
    MODE_RESOLUTION:int = 2

    # Constructor
    def __init__(self, parent: wxMainFrame):
        wxOwnPanel.__init__(self, parent)
        self.mode_ = self.MODE_NONE

        mySizer = wx.BoxSizer(wx.VERTICAL)
        self.labelMode_ = wx.StaticText(self, label=GUIConsts.STR_MODE)
        mySizer.Add(self.labelMode_, 0, wx.ALIGN_CENTER, 50)  # pyright: ignore[reportUnknownMemberType]
        self.labelCount_ = wx.StaticText(self, label="Outils")
        mySizer.Add(self.labelCount_, 0, wx.ALL, 5)  # pyright: ignore[reportUnknownMemberType]
        mySizer.Add(wx.Button(self, label="Pinceau"), 0, wx.EXPAND | wx.ALL, 5)  # pyright: ignore[reportUnknownMemberType]
        mySizer.AddStretchSpacer()
        self.SetSizer(mySizer)

        # Needs to draw panel's border
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]

    # Set app; mode => set controls' state
    def setMode(self, mode:int = MODE_NONE):
        self.mode_ = mode
        self.labelMode_.SetLabel(f"{GUIConsts.STR_MODE}" if self.mode_ == self.MODE_NONE else f"{GUIConsts.STR_MODE} : {GUIConsts.STR_MODE_CREATION if self.mode_ == self.MODE_CREATION else GUIConsts.STR_MODE_RESOLUTION}")

    # Set child canvas
    def setCanvas(self, canvas: wxSolverCanvas):
        self.canvas_ = canvas

    # Redraw the panel
    def OnPaint(self, event : wx.Event):
        self.labelCount_.SetLabel(f"{GUIConsts.STR_FILLED} : {self.canvas_.sudoku_.count_} / {ARRAY_SIZE}")

        dc = wx.PaintDC(self)
        pen = wx.Pen(self.canvas_.theme_[GUITheme.colourID.ID_TB_BORDER].other, 1, wx.PENSTYLE_SOLID)
        dc.SetPen(pen)
        size = self.GetClientSize()
        dc.DrawLine(0, 0, 0, size.height-1)     # draw the left border using using defined colour

# wxSolverFrame - App. main frame
#
class wxSolverFrame(wxMainFrame):
    def __init__(self, params: options):
        wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = wx.DEFAULT_FRAME_STYLE, size=wx.Size(450, 300))

        # sudoku solver canvas
        self.canvas_ = wxSolverCanvas(self, params)

        # Sidebar
        self.sidebar_ = wxSidebarPanel(self)
        self.sidebar_.setCanvas(self.canvas_)
        self.sidebar_.SetMinSize(wx.Size(220, -1))
        self.sidebar_.SetBackgroundColour(self.canvas_.theme_[GUITheme.colourID.ID_TB_BK].other)


        # Add the 2 panels to the frame's sizer
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        mainSizer.Add(self.canvas_, 1, wx.EXPAND)       # pyright: ignore[reportUnknownMemberType]
        mainSizer.Add(self.sidebar_, 0, wx.EXPAND)# pyright: ignore[reportUnknownMemberType]
        self.SetSizer(mainSizer)

        # Bind menu events to handler
        self.Bind(wx.EVT_MENU, self.OnMenu)  # pyright: ignore[reportUnknownMemberType]

        # Let's go !!!
        self.Centre()
        self.Show()

    # GUI initialization
    #
    def initialize(self):
        self.canvas_.initialize()

    # Theme just changed
    #
    def themeChanged(self):
        self.sidebar_.SetBackgroundColour(self.canvas_.theme_[GUITheme.colourID.ID_TB_BK].other)

    # End drawings
    #
    def end(self):
        self.canvas_.end()

    # Click on a menu item
    #
    def OnMenu(self, event:wx.MenuEvent):
        menuId = event.GetId()

        match menuId:
            case menuConsts.ID_SIDEBAR:
                self.onToggleSidebar()
            case wx.ID_EXIT:
                self.Destroy()
            case _:
                self.canvas_.OnMenu(event)  # Other events are handled by the canvas panel


    # Show / hide the side bar
    #
    def onToggleSidebar(self):
        self.sidebar_.Show(not self.sidebar_.IsShown())
        self.Layout()

# EOF
