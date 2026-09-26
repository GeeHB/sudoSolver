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
import os
import sys
import time
from typing import override

try :
    import wx
except ModuleNotFoundError:
    print("wxPython library is not installed")
    sys.exit(0)

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
    # Constructor
    #
    def __init__(self, params : options):
        #wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = (wx.CAPTION & wx.RESIZE_BORDER))
        wx.Frame.__init__(self, None, title = APP_SHORT_NAME, style = wx.DEFAULT_FRAME_STYLE)
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

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self.Show()

        # Associate event to handlers
        #
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLButtonUp)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]

        self.fromFile("/home/jhb/Nextcloud/personnel/JHB/dev/python/sudoSolver/sudokus/diverto09-6.txt", False)

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

    # User clicked  with left button
    #
    def OnLButtonUp(self, event : wx.MouseEvent):
        self.edition_.prevPos_ = copy.deepcopy(self.edition_.currentPos_)   # // copy constructor

        newPos : tuple[int,int] = self.mousePosition(pos=(event.x, event.y))
        if self.edition_.currentPos_.moveTo(pos=newPos) :
            self._edit_updatePos(self.edition_.prevPos_, self.edition_.currentPos_)

    # Draw the window
    #
    def OnPaint(self, event : wx.Event):
        if self.memDC_ is not None and self.memDC_.IsOk():
            bmpSize : wx.Size = self.memDC_.GetSize()
            paintDC = wx.PaintDC(self)
            paintDC.Blit(0, 0, bmpSize.width, bmpSize.height, self.memDC_, 0, 0)

    # Window's size just changed
    #
    def OnSize(self, event : wx.SizeEvent):
        # Resize elements
        self.newWindowSize(event.Size.width, event.Size.height)
        self.clientSize_ = event.Size
        self.font_.SetPixelSize(wx.Size(0, self.fontSize_))

        if self.memDC_ :
            self.memDC_.SelectObject(wx.NullBitmap) # Free previous bitmap if any
            self.memDC_ = None

        # Create memory DC with bitmap
        self._draw_StartUp()

        # Numbers are centered !
        self._draw_StartUp()
        if self.memDC_ is not None and self.memDC_.IsOk() :
            self.memDC_.SetFont(self.font_)
            dims : wx.Size = self.memDC_.GetTextExtent("O")
            self.textOffsets_ = wx.Size(math.floor((self.extSquareWidth_ - dims.width) / 2), math.floor((self.extSquareWidth_ - dims.height) / 2))

        # Redraw the whole array
        self._draw_background()
        self.draw()

    #
    #  drawings
    #

    @override
    def _draw_StartUp(self):
        if self.memDC_ is None :
            bmp = wx.Bitmap()
            bmp.CreateWithDIPSize(self.clientSize_, self.GetDPIScaleFactor())
            self.memDC_ = wx.MemoryDC(bmp)
            self.memDC_.SetFont(self.font_)
            self.memDC_.SetBackground(wx.Brush(self.colours_[self.ColourID.ID_BK].other))
            self.memDC_.Clear()

    @override
    def _draw_End(self):
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
                    x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + self.offsets_[0]
                    y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + self.offsets_[1] + GUIConsts.MENUBAR_HEIGHT
                    self.memDC_.DrawLine(x, y, x, y + self.extSquareWidth_)
                    self.memDC_.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            # ... large ext. borders
            #
            penLarge = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, GUIConsts.EXT_BORDER_THICK, wx.PENSTYLE_SOLID)
            self.memDC_.SetPen(penLarge)
            lSquare = self.extSquareWidth_ * 3

            for line in range(3):
                for row in range(3):
                    x = GUIConsts.DELTA_W + row * lSquare + self.offsets_[0]
                    y = GUIConsts.DELTA_H + line * lSquare + self.offsets_[1] + GUIConsts.MENUBAR_HEIGHT
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
        x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[0]
        y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsets_[1] + GUIConsts.MENUBAR_HEIGHT

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
    def convertColours(self):
        for id in range(len(self.colours_)):
            self.colours_[id].other = wx.Colour(
                self.colours_[id].r,
                self.colours_[id].g,
                self.colours_[id].b,
                self.colours_[id].a)
# EOF
