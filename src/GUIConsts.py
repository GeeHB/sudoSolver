# coding=UTF-8
#
#   File        :   GUIConsts.py
#
#   Author      :   GeeHB
#
#   Description :   Shared consts for graphocs and drawings
#

TRANSP_COLOUR = (224, 224, 224)

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

TXT_FONT_NAME          = 'Helvetica,Arial'                 # for the filename
TXT_FONT_SIZE          = 25
TXT_FONT_POS_X         = 35
TXT_FONT_POS_Y         = 5

# Timers
#
TIMER_ID_SELECTED:int = 100
TIMER_RATE_SELECTED:int = 750 # Blinking rate in ms

MSG_HIDE_RATE: int = 2000 # Hide the filename

#
#  str
#
STR_NEW:str = "New sudoku"
STR_LOAD:str = "Open sudoku"
STR_SAVE:str = "Save sudoku"
STR_EXIT:str = "Exiting app."

STR_WILDCARD:str= "Text Files (*.txt)|*.txt|All Files (*.*)|*.*"
STR_NOT_SAVED:str = "Current content has not been saved.\nDo you want to proceed?"
STR_NO_SOLUTION:str = "No solution found."

#EOF
