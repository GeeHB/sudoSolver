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
SQUARE_SIDE_BASE:int    = 60
SQUARE_SIDE:int         = 60   # Initial external size of a square element
SQUARE_MIN:int          = 10   # Minimal square size

DELTA_W:int             = 10   # Offsets
DELTA_H:int             = 10

EXT_BORDER_THICK:int    = 3    # Thickness of external border

# Help matrix
#
HELP_SPACE:int          = 80
HELP_BORDER:int         = 2
HELP_RATIO:int          = 2

# Tags / Hypothesis
TAG_MIN_SIZE:int        = 6     # Dims
TAG_MAX_SIZE:int        = 20
TAG_PADDING:int         = 4

TAG_COMBO_BORDER:int    = 6     # border in the combobox
TAG_COMBO_HEIGHT:int    = 26
TAG_COMBO_SEL_COLOUR    = (195, 195, 195)
TAG_COMBO_NO_COLOUR_STR:str = "no tag"


# Elements'text font sizes (in pixels) and names
#

DEFAULT_FONT_NAME:str = "Helvetica"
DEFAULT_FONT_SIZE:int = 25

#CANVAS_FONT_NAME:str    = 'Herculanum,Papyrus,Helvetica'    # The first font in the list ...
#CANVAS_FONT_NAME:str    = 'Source Code Pro'
#CANVAS_FONT_SIZE:int    = 25                                # default size

#TXT_FONT_NAME:str       = 'Helvetica,Arial'                 # for the filename
#TXT_FONT_SIZE:int       = 12
TXT_FONT_POS_X:int      = 35
TXT_FONT_POS_Y:int      = 5

# Timers
#
TIMER_ID_SELECTED:int     = 100
TIMER_RATE_SELECTED:int   = 750 # Blinking rate in ms

TIMER_ID_NOTIFYING:int    = 101
TIMER_RATE_NOTIFYING:int  = 500 # Blinking rate in ms
BLINK_COUNT_MODIFYING:int = 20 # Max. count of blinking for notifications

PY_MSG_HIDE_RATE:int      = 750 # Hide the filename (for pygame only)

#
#  str
#
STR_CREATE:str = "Sudoku creation"
STR_EXIT:str = "Exiting app."
STR_LOAD:str = "Open sudoku"
STR_NEW:str = "New sudoku"
STR_SAVE:str = "Save sudoku"


STR_MODIFIED_ARRAY:str= "The array has been modified. All modified elements will be turned into 'original' elements.\nDo you want to proceed?"
STR_WILDCARD:str= "Text Files (*.txt)|*.txt|All Files (*.*)|*.*"
STR_NOT_SAVED:str = "Current content has not been saved.\nDo you want to proceed?"
STR_NO_SOLUTION:str = "No solution found."

STR_SIDEBAR:str = "Sidebar"
STR_MODE:str = "mode"
STR_MODE_CREATION:str = "Creation"
STR_MODE_RESOLUTION:str = "Resolution"

STR_FILLED:str = "Filled"

#EOF
