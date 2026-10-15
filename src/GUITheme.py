# coding=UTF-8
#
#   File        :   GUITheme.py
#
#   Author      :   GeeHB
#
#   Description :   Themes management
#
from enum import IntEnum, auto
from typing import Any

from GUIConsts import CANVAS_FONT_NAME, CANVAS_FONT_SIZE, TXT_FONT_NAME, TXT_FONT_SIZE


# IDs of colours used by app.
#
class colourID(IntEnum):
    ID_TB_BK = 0
    ID_TB_BORDER = auto()
    ID_TB_TXT = auto()
    ID_CANVAS_BK = auto()
    ID_FRAME_BORDER = auto()    # Frame borders and bkgrnd
    ID_FRAME_BK_EVEN = auto()
    ID_FRAME_BK_ODD = auto()
    ID_BK_FILENAME = auto()
    ID_DEFAULT_TXT = auto()  # Text colours
    ID_ORIGINAL_TXT = auto()
    ID_OBVIOUS_TXT = auto()
    ID_SEL_BK = auto()      # Selected text and bkgrnd
    ID_SEL_TXT = auto()
    ID_TAG_1 = auto()
    ID_TAG_2 = auto()
    ID_TAG_3 = auto()
    ID_TAG_4 = auto()
    ID_COLOUR_COUNT = auto()    # Last item

#  Themes with colours in RGB
#

DEF_THEME_NAME = "One Light"

# Dict. of themes
#
colourThemes = {
    "Kosmos": {
        "fonts" : {
            "canvas" : "Helvetica",
            "message" : "Helvetica"
            },
        "colours" : [
            (53, 57, 68),
            (83, 86, 93),
            (216, 187, 204),
            (53, 57, 68),
            (53, 57, 68),
            (54, 80, 101),     # even
            (36, 40, 53),      # odd
            (216, 187, 204),
            (216, 187, 204),    # Def. text
            (234, 150, 69),
            (135,220,127),
            (83, 86, 83),       # Selected text and bkgrnd
            (216, 187, 204),
            (255,255,0),
            (0,0,255),
            (0,255,0),
            (255,0,0),
            ],
    },
    "One Light": {
        "fonts" : {
            "canvas" : "Source Code Pro",
                "message" : "Helvetica"
            },
        "colours" : [
            (235, 235, 236),
            (201, 201, 202),
            (80, 88, 104),
            (250, 250, 250),
            (250, 250, 250),
            (239, 239, 240),
            (202, 202, 202),
            (220, 220, 245),
            (80, 88, 104),
            (192, 132, 83),
            (104,160,91),
            (212, 219, 244),
            (250, 250, 250),
            (255,255,0),
            (0,0,255),
            (0,255,0),
            (255,0,0),
            ],
    },
    "Zarina": {
        "fonts" : {
            "canvas" : "DejaVu",
            "message" : "Helvetica"
            },
        "colours" : [
            (230, 230, 255),
            (81, 154, 186),
            (255,255,255),
            (230, 230, 255),
            (81, 154, 186),
            (230, 230, 255),
            (230, 230, 255),
            (220, 220, 245),
            (64, 64, 64),
            (248, 128, 112),
            (81, 154, 186),
            (50, 50, 255),
            (255, 255, 255),
            (255,255,0),
            (0,0,255),
            (0,255,0),
            (255,0,0),
            ],
    }
}

# ownColour - General and portable colour definition
#
class ownColour:
    r : int
    g : int
    b : int
    a : int

    def __init__(self, rgb : tuple[int,int,int] | None, alpha : int | None = None):
        if rgb is not None:
            self.r = rgb[0]
            self.g = rgb[1]
            self.b = rgb[2]
        self.a = alpha if alpha is not None else 255
        self.other : Any = None

# Informations about graphic theme
#
class ownTheme:
    def __init__(self, name:str | None = None):
        self.name_:str = "" if name is None else name
        self.canvasFontName_:str = CANVAS_FONT_NAME
        self.canvasFontSize_:int= CANVAS_FONT_SIZE
        self.textFontName_:str = TXT_FONT_NAME
        self.textFontSize_:int = TXT_FONT_SIZE
        self.colours_: list[ownColour] = []

    # Properties
    #

    # Name of current theme
    @property
    def name(self)->str:
        return self.name_
    @name.setter
    def name(self, name: str):
        self.name_ = name

    # Canvas font
    @property
    def canvasFontName(self)->str:
        return self.canvasFontName_
    @canvasFontName.setter
    def canvasFontName(self, name: str):
        self.canvasFontName_ = name  if len(name)>0 else CANVAS_FONT_NAME
    @property
    def canvasFontSize(self)->int:
        return self.canvasFontSize_
    @canvasFontSize.setter
    def canvasFontSize(self, value: int):
        self.canvasFontSize_ = value

    # Default text font
    @property
    def textFontName(self)->str:
        return self.textFontName_
    @textFontName.setter
    def textFontName(self, name: str):
        self.textFontName_ = name  if len(name)>0 else TXT_FONT_NAME
    @property
    def textFontSize(self)->int:
        return self.textFontSize_

    # Clear the list
    def clear(self):
        self.colours_.clear()

    # Add an item
    def append(self, value:ownColour):
        self.colours_.append(value)

    # Access
    #
    def __getitem__(self, index:int)->ownColour:
        if index < 0 or index>=len(self.colours_):
            raise IndexError
        return self.colours_[index]

    def __setitem__(self, index:int, value: ownColour):
        size:int = len(self.colours_)
        if index < 0 or index>size:
            raise IndexError

        if index < size:
            self.colours_[index] = value    # Modify
        else:
            self.append(value)

    # len / size of internal colours list
    def __len__(self)->int:
        return len(self.colours_)
# EOF
