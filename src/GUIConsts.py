# coding=UTF-8
#
#   File        :   GUIConsts.py
#
#   Author      :   GeeHB
#
#   Description :   Shared consts for graphocs and drawings
#

#  App colours in RGB
#

COLOUR_WND_BK = (250, 250, 250)

COLOUR_BORDER = COLOUR_WND_BK
COLOUR_BK_ODD = (239, 239, 240)
COLOUR_BK_EVEN = (202, 202, 202)

COLOUR_BK_FILENAME = (220, 220, 245)

COLOUR_DEF_TXT = (80, 88, 104)
COLOUR_ORIGINAL = (192, 132, 83)
COLOUR_OBVIOUS = (104,160,91)

COLOUR_SEL_BK = (212, 219, 244)
COLOUR_SEL_TXT = COLOUR_DEF_TXT

# Old
"""
COLOUR_WND_BK = (230, 230, 255)

COLOUR_BORDER = (81, 154, 186)
COLOUR_BK_ODD = (230, 230, 255)
COLOUR_BK_EVEN = (230, 230, 255)

COLOUR_BK_FILENAME = (220, 220, 245)

COLOUR_TXT = (64, 64, 64)
COLOUR_ORIGINAL = (248, 128, 112)
COLOUR_OBVIOUS = COLOUR_BORDER

COLOUR_SEL_BK = (50, 50, 255)
COLOUR_SEL_TXT = (255, 255, 255)
"""

COLOUR_YELLOW = (255,255,0)
COLOUR_BLUE = (0,0,255)
COLOUR_GREEN=(0,255,0)
COLOUR_RED=(255,0,0)

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
