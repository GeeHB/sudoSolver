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
        wx.Frame.__init__(self, None)
        solver.solver.__init__(self, params)

    # GUI initialization
    #
    @override
    def initialize(self):
        solver.solver.initialize(self)

        self.SetBackgroundColour(self.colours_[self.ColourID.ID_BK].other)  # Set background color

        # Associate event to handlers
        #
        self.Bind(wx.EVT_PAINT, self.OnPaint)  # pyright: ignore[reportUnknownMemberType]
        self.Bind(wx.EVT_SIZE, self.OnSize)  # pyright: ignore[reportUnknownMemberType]


    #
    # Event handlers
    #

    # Draw the window
    #
    def OnPaint(self, event : wx.Event):
        self.drawBackground()

    # Window's size just changed
    #
    def OnSize(self, event : wx.SizeEvent):
        self.resizeWindow(event.Size.width, event.Size.height)

    #
    #  drawings
    #

    # Draw background, frames and borders
    #
    @override
    def drawBackground(self):
        if 0 != self.extSquareWidth_ :
            dc = wx.PaintDC(self)
            dc = wx.GCDC(dc)

            # thin borders ...
            #
            pen = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, 1, wx.PENSTYLE_SOLID)
            dc.SetPen(pen)

            for line in range(LINE_COUNT):
                for row in range(ROW_COUNT):
                    x = GUIConsts.DELTA_W + row * self.extSquareWidth_
                    y = GUIConsts.MENUBAR_HEIGHT + GUIConsts.DELTA_H + line * self.extSquareWidth_
                    dc.DrawLine(x, y, x, y + self.extSquareWidth_)
                    dc.DrawLine(x, y + self.extSquareWidth_, x + self.extSquareWidth_, y + self.extSquareWidth_)

            # ... large ext. borders
            #
            penLarge = wx.Pen(self.colours_[self.ColourID.ID_BORDER].other, GUIConsts.EXT_BORDER_THICK, wx.PENSTYLE_SOLID)
            dc.SetPen(penLarge)
            lSquare = self.extSquareWidth_ * 3

            for line in range(3):
                for row in range(3):
                    x = GUIConsts.DELTA_W + row * lSquare
                    y = GUIConsts.MENUBAR_HEIGHT + GUIConsts.DELTA_H + line * lSquare
                    dc.DrawLine(x, y,x, y + lSquare)
                    dc.DrawLine(x, y + lSquare,x + lSquare, y + lSquare)
                    dc.DrawLine(x + lSquare, y + lSquare,x + lSquare, y)
                    dc.DrawLine(x + lSquare, y, x, y)

            self.update()

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
