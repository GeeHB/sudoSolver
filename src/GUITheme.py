# coding=UTF-8
#
#   File        :   GUITheme.py
#
#   Author      :   GeeHB
#
#   Description :   Themes management
#

from typing import Any

from GUIConsts import ELT_FONT_NAME


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

# Information about current theme
#
class GUITheme:
    def __init__(self, name:str | None = None):
        self.name_:str = "" if name is None else name
        self.fontFaceName_:str = ELT_FONT_NAME
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

    # Name of the font to use
    @property
    def fontName(self)->str:
        return self.fontFaceName_
    @fontName.setter
    def fontName(self, name: str):
        self.fontFaceName_ = name  if len(name)>0 else ELT_FONT_NAME

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


# EOF
