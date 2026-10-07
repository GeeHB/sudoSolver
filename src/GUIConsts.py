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

COLOUR_BORDER = (81, 154, 186)
COLOUR_BK = (230, 230, 255)
COLOUR_BK_FILENAME = (220, 220, 245)
COLOUR_TXT = (64, 64, 64)
COLOUR_HILITE = (248, 128, 112)
COLOUR_OBVIOUS = COLOUR_BORDER
COLOUR_SEL_BK = (50, 50, 255)
COLOUR_SEL_TXT = (255, 255, 255)

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

TAG_MIN_SIZE:int        = 6


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
BLINK_RATE : int = 750 # Blinking rate in ms
MSG_HIDE_RATE : int = 2000 # Hide the filename

#
#  str
#
STR_NEW: str = "New sudoku"
STR_LOAD: str = "Open sudoku"
STR_SAVE: str = "Save sudoku"
STR_EXIT:str = "Exiting app."

STR_NOTSAVED:str = "Current content has not been saved.\nDo you want to proceed?"

#EOF
