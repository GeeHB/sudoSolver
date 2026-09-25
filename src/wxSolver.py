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

        self.font_ = wx.Font(GUIConsts.ELT_FONT_SIZE,
                        wx.FONTFAMILY_DEFAULT,
                        wx.FONTSTYLE_NORMAL,
                        wx.FONTWEIGHT_NORMAL,
                        faceName = GUIConsts.ELT_FONT_NAME)

        solver.solver.__init__(self, params)
        self.dc_ = None
        self.textOffsets_ : wx.Size = wx.Size(0,0)

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self.SetBackgroundColour(self.colours_[self.ColourID.ID_BK].other)  # Set background color
        self.Show()

        # Associate event to handlers
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]

        self.fromFile("/home/jhb/Nextcloud/personnel/JHB/dev/python/sudoSolver/sudokus/diverto09-6.txt", False)

    #
    # Event handlers
    #

    # Draw the window
    #
    def OnPaint(self, event : wx.Event):
        self.displayStartUp()
        #self.drawBackground()
        self.draw(redrawBackground=True)
        self.displayEnd()

    # Window's size just changed
    #
    def OnSize(self, event : wx.SizeEvent):
        #print(f"x:{event.Size.width} - y:{event.Size.height}")
        self.newWindowSize(event.Size.width, event.Size.height)
        self.font_.SetPixelSize(wx.Size(0, self.fontSize_))

        # Numbers are centered !
        dc = wx.ClientDC(self)
        dc.SetFont(self.font_)
        dims : wx.Size = dc.GetTextExtent("O")
        self.textOffsets_ = wx.Size(math.floor((self.extSquareWidth_ - dims.width) / 2), math.floor((self.extSquareWidth_ - dims.height) / 2))

    #
    #  drawings
    #

    @override
    def displayStartUp(self):
        dc = wx.PaintDC(self)
        self.dc_ = wx.GCDC(dc)

        self.dc_.SetTextForeground(self.colours_[self.ColourID.ID_TXT].other)
        self.dc_.SetFont(self.font_)

    @override
    def displayEnd(self):
        self.dc_ = None

    # Draw background, frames and borders
    #
    @override
    def drawBackground(self):
        if self.dc_ is not None and 0 != self.extSquareWidth_ :
            # thin borders ...
            #
            pen = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, 1, wx.PENSTYLE_SOLID)
            self.dc_.SetPen(pen)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + self.offsetX_
                    y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + self.offsetY_ + GUIConsts.MENUBAR_HEIGHT
                    self.dc_.DrawLine(x, y, x, y + self.extSquareWidth_)
                    self.dc_.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            # ... large ext. borders
            #
            penLarge = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, GUIConsts.EXT_BORDER_THICK, wx.PENSTYLE_SOLID)
            self.dc_.SetPen(penLarge)
            lSquare = self.extSquareWidth_ * 3

            for line in range(3):
                for row in range(3):
                    x = GUIConsts.DELTA_W + row * lSquare + self.offsetX_
                    y = GUIConsts.DELTA_H + line * lSquare + self.offsetY_ + GUIConsts.MENUBAR_HEIGHT
                    self.dc_.DrawLine(x, y,x, y + lSquare)
                    self.dc_.DrawLine(x, y + lSquare,x + lSquare, y + lSquare)
                    self.dc_.DrawLine(x + lSquare, y + lSquare,x + lSquare, y)
                    self.dc_.DrawLine(x + lSquare, y, x, y)


    # Draw/erase a single element and its background
    #
    @override
    def drawSingleElement(self, row:int, line:int, value:int | None, bkColourID:int, txtColourID:int):
        # too small to be drawn ?
        if self.dc_ is None or 0 == self.extSquareWidth_ :
            return

        # top-left corner position
        x = GUIConsts.DELTA_W + row * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsetX_ + self.textOffsets_.x
        y = GUIConsts.DELTA_H + line * self.extSquareWidth_ + GUIConsts.EXT_BORDER_THICK + self.offsetY_ + GUIConsts.MENUBAR_HEIGHT + self.textOffsets_.y

        # Erase background
        self.dc_.SetBrush(wx.Brush(self.colours_[self.ColourID.ID_BK].other))
        self.dc_.SetPen(wx.TRANSPARENT_PEN)
        self.dc_.DrawRectangle(x, y, self.fontSize_, self.fontSize_)

        # The value (if valid)
        if value is not None :
            self.dc_.DrawText(str(value), x, y)

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
