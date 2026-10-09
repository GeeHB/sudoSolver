# coding=UTF-8
#
#   File        :   GUIConsts.py
#
#   Author      :   GeeHB
#
#   Description :   Shared consts for graphocs and drawings
#

from enum import IntEnum, auto


# IDs of colours used by app.
#
class colourID(IntEnum):
    ID_WINDOW_BK = 0
    ID_FRAME_BORDER = 1    # Frame borders and bkgrnd
    ID_FRAME_BK_EVEN = 2
    ID_FRAME_BK_ODD = 3
    ID_BK_FILENAME = 4
    ID_DEFAULT_TXT = 5  # Text colours
    ID_ORIGINAL_TXT = 6
    ID_OBVIOUS_TXT = 7
    ID_SEL_BK = 7      # Selected text and bkgrnd
    ID_SEL_TXT = 9
    ID_TAG_1 = 10
    ID_TAG_2 = 11
    ID_TAG_3 = 12
    ID_TAG_4 = 13
    ID_COLOUR_COUNT = auto()    # Last item

#  Themes with colours in RGB
#

colourThemes = {
    "One Light": [
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
    "Zarina": [
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
        ]
    }

DEF_THEME_NAME = "One Light"

# Positions and dimensions in pixels
#
SQUARE_SIDE_BASE        = 60
SQUARE_SIDE             = 60   # Initial external size of a square element

STATS_FRAME_WIDTH       = 0    # Width in pixels of stats'frame

SQUARE_MIN              = 10   # Minimal square size

DELTA_W                 = 10   # Offsets
DELTA_H                 = 10

EXT_BORDER_THICK        = 3    # Thickness of external border

# Tags / Hypothesis
TAG_MIN_SIZE:int        = 6     # Dims
TAG_MAX_SIZE:int        = 20

TAG_PADDING:int         = 4

# Elements'text font sizes (in pixels) and names
#
ELT_FONT_NAME           = 'Herculanum,Papyrus,Helvetica'    # The first font in the list ...
ELT_FONT_SIZE           = 35                                # default size

FILE_FONT_NAME          = 'Helvetica,Arial'                 # for the filename
FILE_FONT_SIZE          = 25
FILE_FONT_POS_X         = 35
FILE_FONT_POS_Y         = 5

# Timers frequencies
#
BLINK_ID:int = 100
BLINK_RATE: int = 750 # Blinking rate in ms

MSG_HIDE_RATE: int = 2000 # Hide the filename

#
#  str
#
STR_NEW: str = "New sudoku"
STR_LOAD: str = "Open sudoku"
STR_SAVE: str = "Save sudoku"
STR_EXIT:str = "Exiting app."

STR_NOTSAVED:str = "Current content has not been saved.\nDo you want to proceed?"

#EOF
