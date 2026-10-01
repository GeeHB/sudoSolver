# coding=UTF-8
#
#   File        :   wxSolver.py
#
#   Author      :   GeeHB
#
#   Description :   draw sudoku using the wxPython library
#                   Fedora : sudo dnf install python3-wxpython4
#
from curses import KEY_ENTER
import math
import sys
from typing import override

try :
    import wx  # pyright: ignore[reportMissingTypeStubs]
except ModuleNotFoundError:
    print("wxPython library is not installed")
    sys.exit(0)

import GUIConsts
import menuConsts
import solver
from element import element
from options import (
    APP_SHORT_NAME,
    arrayComplexity,
    options,
)
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
)
from sharedTools import statusbits


# wxSolverApp - Abstract class for application
#
class wxSolverApp(wx.App, solver.solverApp):
    # Constructor
    #
    def __init__(self, params : options):
        wx.App.__init__(self)  # pyright: ignore[reportUnknownMemberType]
        solver.solverApp.__init__(self, params)

        self.solver_ : wxSolver = wxSolver(params)

    # GUI initialization
    #
    @override
    def initialize(self):
        self.solver_.initialize()

    # Start drawings / UI
    #
    @override
    def start(self):
        self.solver_.Show()
        self.MainLoop()  # pyright: ignore[reportUnknownMemberType]

    # End drawings
    #
    @override
    def end(self):
        self.solver_.end()

# wxSolver - Abstract class for GUI sudoku solvers
#
class wxSolver(wx.Frame, solver.solver):
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

    # Constructor
    #
    def __init__(self, params : options):
        self.state_ : statusbits.statusBits = statusbits.statusBits(self.ARRAY_NEW)
        wx.Log.SetLogLevel(wx.LOG_Error)  # pyright: ignore[reportUnknownMemberType]

        wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = wx.DEFAULT_FRAME_STYLE)
        self.panel_ = wx.Panel(self, wx.ID_ANY)     # to receive keyboard focus

        solver.solver.__init__(self, params)

        # Display
        self.memDC_ : wx.MemoryDC | None = None # all display are made in a memory DC
        self.directDraw_ = False
        self.clientSize_ : wx.Size = wx.Size(0,0)
        self.textOffsets_ : wx.Size = wx.Size(0,0)  # for text in array
        self.font_ = wx.Font(GUIConsts.ELT_FONT_SIZE,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL,
                        faceName = GUIConsts.ELT_FONT_NAME)
        self.blinkTimer_ : wx.Timer = wx.Timer(self)

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self._menu_createBar()

        # Associate event to handlers
        #
        self.panel_.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  # pyright: ignore[reportUnknownMemberType]

        # binded twice isnce panel and frame both can intercept a click !
        self.panel_.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]

        self.Bind(wx.EVT_MENU, self.OnMenu)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.blinkTimer_) # pyright: ignore[reportUnknownMemberType]

        self.panel_.SetFocus()
        self.Show()

    # Set/change the current array's filename
    #
    @override
    def _setFilename(self, fileName:str, create:bool = False):
        solver.solver._setFilename(self, fileName, create)

        title : str = APP_SHORT_NAME
        if len(fileName) > 0:
            title = title + " - " + fileName

        self.SetTitle(title)

    #
    # Event handlers
    #

    def OnMenu(self, event:wx.MenuEvent):
        menuId = event.GetId()

        match menuId:
            case menuConsts.ID_FILE_NEW_EMPTY | menuConsts.ID_FILE_NEW_EASY | menuConsts.ID_FILE_NEW_MEDIUM | menuConsts.ID_FILE_NEW_HARD :
                self._menu_fileNewArray(menuId)
            case wx.ID_OPEN:
                self._menu_fileOpen()
            case wx.ID_SAVE:
                self._menu_fileSave()

            case menuConsts.ID_EDIT_MODIFY:
                self._edit_start()

            case menuConsts.ID_EDIT_DONE:
                self._edit_stop()

            case menuConsts.ID_SOLVE_OBVIOUS:
                self._menu_findOviousValues()
            case menuConsts.ID_SOLVE_RESOLVE_SINGLE:
                    self._menu_resolveSingleThread()
            case menuConsts.ID_SOLVE_RESOLVE_MULTI:
                    self._menu_resolveMultiThreaded()
            case menuConsts.ID_SOLVE_REVERT:
                    self._menu_revertArray()

            case wx.ID_EXIT:
                self.Close(True)
            case _:
                pass

    # Keyboard events
    #
    def OnKeyDown(self, event :  wx.KeyEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            self._edit_array(event)
            return

        event.Skip()  # Allow other handlers to process the key

    # User clicked  with left button
    #
    def OnLButtonUp(self, event : wx.MouseEvent):
        if self.state_.isSet(self.ARRAY_EDITING) :
            self.edition_.move()
            newPos : tuple[int,int] = self._mouse_translatePosition(pos=(event.x, event.y))

            if self.edition_.currentPos_.moveTo(pos=newPos):
                self._edit_selChanged()

            return

        event.Skip()  # Allow other handlers to process the key

    # Draw the window
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
        self.font_.SetPixelSize(wx.Size(0, self.fontSize_))

        if self.memDC_ :
            self.memDC_.SelectObject(wx.NullBitmap) # Free previous bitmap if any
            self.memDC_ = None

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

    def OnTimer(self, event : wx.Event):
        self._edit_blink()

    #
    #  drawings
    #

    @override
    def _draw_startUp(self):
        if self.memDC_ is None :
            bmp = wx.Bitmap()
            bmp.CreateWithDIPSize(self.clientSize_, self.GetDPIScaleFactor())
            self.memDC_ = wx.MemoryDC(bmp)
            self.memDC_.SetFont(self.font_)
            self.memDC_.SetBackground(wx.Brush(self.colours_[self.ColourID.ID_BK].other))
            self.memDC_.Clear()

    @override
    def _draw_end(self):
        if not self.directDraw_ :
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
            pen = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, 1, wx.PENSTYLE_SOLID)
            self.memDC_.SetPen(pen)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = row * self.extSquareWidth_ + self.offsets_[0]
                    y = line * self.extSquareWidth_ + self.offsets_[1]
                    self.memDC_.DrawLine(x, y, x, y + self.extSquareWidth_)
                    self.memDC_.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            # ... large ext. borders
            #
            penLarge = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, GUIConsts.EXT_BORDER_THICK, wx.PENSTYLE_SOLID)
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
    def _draw_singleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int):
        # too small to be drawn ?
        if self.memDC_ is None or 0 == self.extSquareWidth_ :
            return

        # top-left corner position
        x = row * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[0]
        y = line * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[1]

        # Erase background
        self.memDC_.SetBrush(wx.Brush(self.colours_[bkColourID].other))
        self.memDC_.SetPen(wx.TRANSPARENT_PEN)
        self.memDC_.DrawRectangle(x, y, self.intSquareWidth_, self.intSquareWidth_)

        # The value (if valid)
        if value is not None :
            self.memDC_.SetTextForeground(self.colours_[txtColourID].other)
            self.memDC_.DrawText(str(value), x + self.textOffsets_.x, y + self.textOffsets_.y)

    # Convert colour objects from ownColour to wx.Colour
    #
    @override
    def _draw_convertColours(self):
        for id in range(len(self.colours_)):
            self.colours_[id].other = wx.Colour(
                self.colours_[id].r,
                self.colours_[id].g,
                self.colours_[id].b,
                self.colours_[id].a)

    # Start edition mode
    #
    @override
    def _edit_start(self, initPos:bool = True):
        self.state_.set(self.ARRAY_EDITING)
        self._menu_setStates()

        # Anything to edit ?
        if len(self.sudoku_.elements_) == 0:
            self.sudoku_.empty()

        if initPos:
            self.edition_.clear(editable = True)    # move to cursor to (0,0)
        else:
            self.edition_.blink = False

        self._edit_blink()
        if not self.blinkTimer_.IsRunning():
            self.blinkTimer_.Start(GUIConsts.BLINK_RATE)

    # End of edition mode
    #
    @override
    def _edit_stop(self):
        self.state_.set(self.ARRAY_EDITING, False)
        if self.edition_.modified:
            self.state_.set(self.ARRAY_MODIFIED, True)

        self._menu_setStates()

        if self.blinkTimer_.IsRunning():
            self.blinkTimer_.Stop()

        self._draw_startUp()
        self._draw_elementSelected(False)
        self._draw_end()


    # Selected item has just changed
    #
    def _edit_selChanged(self):
        self._edit_stop()
        self._edit_updatePos(self.edition_.prevPos_, self.edition_.currentPos_)
        self._edit_start(False)

    def _edit_blink(self):
        self._draw_startUp()
        self._draw_elementSelected(self.edition_.changeBlink())
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
                self._edit_setValue(key - self.KEY_VALUE_1 + 1)
            case self.KEY_VALUE_DEC:
                self._edit_decValue()
            case self.KEY_VALUE_INC:
                self._edit_incValue()
            case self.KEY_REMOVE_VALUE:
                self._edit_removeValue()
            case self.KEY_ENTER | self.KEY_NUM_ENTER:
                self._edit_stop()
                return
            case _:
                pass

        self._edit_selChanged()

    #
    #  Menus
    #

    # Create the menubar
    #
    def _menu_createBar(self):
        # Files popup
        fileMenu = wx.Menu()

        fileNew = wx.Menu()
        fileNew.Append(menuConsts.ID_FILE_NEW_EMPTY, menuConsts.IDM_FILE_NEW_EMPTY)
        fileNew.Append(menuConsts.ID_FILE_NEW_EASY, menuConsts.IDM_FILE_NEW_EASY)
        fileNew.Append(menuConsts.ID_FILE_NEW_MEDIUM, menuConsts.IDM_FILE_NEW_MEDIUM)
        fileNew.Append(menuConsts.ID_FILE_NEW_HARD, menuConsts.IDM_FILE_NEW_HARD)
        fileMenu.Append(wx.ID_ANY, menuConsts.IDM_FILE_NEW, fileNew)

        fileMenu.Append(wx.ID_OPEN)
        fileMenu.Append(wx.ID_SAVE)
        fileMenu.AppendSeparator()
        fileMenu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")

        # Edition
        editMenu = wx.Menu()
        editMenu.Append(menuConsts.ID_EDIT_MODIFY, menuConsts.IDM_EDIT_MODIFY)
        editMenu.Append(menuConsts.ID_EDIT_DONE, menuConsts.IDM_EDIT_DONE)

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
        self.SetMenuBar(self.menuBar_)
        self.menuBar_.Append(fileMenu, menuConsts.IDM_FILE)
        self.menuBar_.Append(editMenu,menuConsts.IDM_EDIT)
        self.menuBar_.Append(solveMenu, menuConsts.IDM_SOLVE)

        self.SetMenuBar(self.menuBar_)
        self._menu_setStates()

    # Change items ' states
    # '
    def _menu_setStates(self):
        #modified : bool = self.state_.isSet(self.ARRAY_MODIFIED)
        editOn : bool = self.state_.isSet(self.ARRAY_EDITING)
        solving : bool = self.state_.isSet(self.ARRAY_SOLVING)

        self.menuBar_.Enable(menuConsts.ID_EDIT_DONE, editOn)

        state : bool = not (editOn or solving)

        self.menuBar_.Enable(menuConsts.ID_FILE_NEW_EMPTY, state)
        self.menuBar_.Enable(menuConsts.ID_FILE_NEW_EASY, state)
        self.menuBar_.Enable(menuConsts.ID_FILE_NEW_MEDIUM, state)
        self.menuBar_.Enable(menuConsts.ID_FILE_NEW_HARD, state)
        self.menuBar_.Enable(wx.ID_OPEN, state)
        self.menuBar_.Enable(wx.ID_SAVE, state)

        self.menuBar_.Enable(menuConsts.ID_EDIT_MODIFY, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_MANUAL, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_OBVIOUS, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_SINGLE, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_RESOLVE_MULTI, state)
        self.menuBar_.Enable(menuConsts.ID_SOLVE_REVERT, state)

    # Create a new or empty array
    #
    def _menu_fileNewArray(self, menuId:int):
        match menuId:
            case menuConsts.ID_FILE_NEW_EASY:
                self.sudoku_.new(arrayComplexity.Easy)
            case menuConsts.ID_FILE_NEW_MEDIUM:
                self.sudoku_.new(arrayComplexity.Medium)
            case menuConsts.ID_FILE_NEW_HARD:
                self.sudoku_.new(arrayComplexity.Hard)
            case _:
                self.sudoku_.new(arrayComplexity.Empty)

        self.state_.assign(self.ARRAY_NEW)
        self._menu_setStates()

        self._draw_update()

    # Load an array
    #
    def _menu_fileOpen(self):
        if self.state_.isSet(self.ARRAY_MODIFIED) and wx.MessageBox("Current content has not been saved! Do you want to proceed?", "Please confirm",
                    wx.ICON_QUESTION | wx.YES_NO, self) == wx.NO:
                return

        with wx.FileDialog(self, "Open sudoku file", wildcard="TXT files (*.txt)|*.txt",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:  # pyright: ignore[reportUnknownArgumentType, reportUnknownVariableType, reportUnknownMemberType]

            if fileDialog.ShowModal() == wx.ID_CANCEL:  # pyright: ignore[reportUnknownMemberType]
                return     # the user changed their mind

        # New file just loaded
        self.fromFile(fileDialog.GetPath())  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]
        self.state_.assign(self.ARRAY_NEW)
        self._menu_setStates()

    # Save current array
    #
    def _menu_fileSave(self):
        path : str = self.filename
        done : bool = False
        wildcard = "Text Files (*.txt)|*.txt|All Files (*.*)|*.*"
        with wx.FileDialog(
            self,
            message="Save sudoku",
            defaultFile=path,
            wildcard=wildcard,
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
        ) as dlg:  # pyright: ignore[reportUnknownVariableType]
            # Affichage et gestion de la réponse
            if dlg.ShowModal() == wx.ID_OK:  # pyright: ignore[reportUnknownMemberType]
                path = dlg.GetPath()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
                ret : str | None = self.sudoku_.save(newFileName=path)  # pyright: ignore[reportUnknownArgumentType]
                done = ret is not None or len(ret)>0  # pyright: ignore[reportArgumentType]

        if done :
            self._setFilename(path)  # pyright: ignore[reportUnknownArgumentType]
            self.state_.assign(self.ARRAY_NEW)
            self._menu_setStates()

    #
    # Resolving
    #

    def _menu_findOviousValues(self):
        if self.sudoku_.IsOk():
            ret : tuple[int,float] = self.sudoku_.findObviousValues()
            if ret[0] > 0:
                self._draw_update()

    def _menu_resolveSingleThread(self):
        if self.sudoku_.IsOk():
            if self._resolve_SingleThreaded():
                self._draw_update()
            else:
                print("Pas de solution")

    def _menu_resolveMultiThreaded(self):
        if self.sudoku_.IsOk():
            self.directDraw_ = True

            if not self._resolve_MultiThreaded():
                print("Pas de solution")

            self.directDraw_ = False
            self._draw_update()

    # Return to original array's state (remove added values)
    #
    def _menu_revertArray(self):
        if self.sudoku_.IsOk():
            self.sudoku_.revert()
            self._draw_update()

# EOF
