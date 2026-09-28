# coding=UTF-8
#
#   File        :   wxSolver.py
#
#   Author      :   GeeHB
#
#   Description :   draw sudoku using the wxPython library
#                   Fedora : sudo dnf install python3-wxpython4
#
import copy
import math
import sys
from typing import override

try :
    import wx  # pyright: ignore[reportMissingTypeStubs]
except ModuleNotFoundError:
    print("wxPython library is not installed")
    sys.exit(0)

import GUIConsts
import solver
from element import element
from options import (
    APP_SHORT_NAME,
    options,
)
from pointer import (
    LINE_COUNT,
    ROW_COUNT,
)


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

    # Constructor
    #
    def __init__(self, params : options):
        #wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = (wx.CAPTION & wx.RESIZE_BORDER))
        wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = wx.DEFAULT_FRAME_STYLE)

        self.panel_ = wx.Panel(self, wx.ID_ANY)     # to receive keyboard focus

        solver.solver.__init__(self, params)

        # Display
        self.memDC_ : wx.MemoryDC | None = None # all display are made in a memory DC
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

        self.Show()

        # Associate event to handlers
        #
        self.panel_.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)  # pyright: ignore[reportUnknownMemberType]

        # binded twice isnce panel and frame both can intercept a click !
        self.panel_.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]

        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.blinkTimer_) # pyright: ignore[reportUnknownMemberType]

        self.panel_.SetFocus()

        self.fromFile("/home/jhb/Nextcloud/personnel/JHB/dev/python/sudoSolver/sudokus/diverto09-6.txt", False)
        self.edition_.editable = True
        self._edit_start()

    # Set/change the current array's filename
    #
    @override
    def setFileName(self, fileName:str, create:bool = False):
        solver.solver.setFileName(self, fileName, create)

        title : str = APP_SHORT_NAME
        if len(fileName) > 0:
            title = title + " - " + fileName

        self.SetTitle(title)

    #
    # Event handlers
    #

    # Keyboard events
    #
    def OnKeyDown(self, event :  wx.KeyEvent):
        if self.edition_.editable:
            keyCode = event.GetKeyCode()
            #print(f"Key : {keyCode}")

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
                case _:
                    pass

            self._edit_selChanged()


            return

        event.Skip()  # Allow other handlers to process the key

    # User clicked  with left button
    #
    def OnLButtonUp(self, event : wx.MouseEvent):
        if self.edition_.editable:
            self.edition_.move()
            newPos : tuple[int,int] = self._mouse_translatePosition(pos=(event.x, event.y))
            if self.edition_.currentPos_.moveTo(pos=newPos):
                self._edit_selChanged()

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
        # Resize elements
        self._draw_newClientSize(event.Size.width, event.Size.height)
        self.clientSize_ = event.Size
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
        self._draw_startUp()
        self._draw_selectedElement(self.edition_.blink())
        self._draw_end()

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
        self.Refresh()

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
    def _edit_start(self):
        if not self.blinkTimer_.IsRunning():
            self.blinkTimer_.Start(GUIConsts.BLINK_RATE)

    # End of edition mode
    #
    @override
    def _edit_stop(self):
        if self.blinkTimer_.IsRunning():
            self.blinkTimer_.Stop()

    # Selected item has just changed
    #
    def _edit_selChanged(self):
        self._edit_stop()
        self._edit_updatePos(self.edition_.prevPos_, self.edition_.currentPos_)
        self._edit_start()

# EOF
