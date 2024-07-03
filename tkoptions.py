# coding=UTF-8
#
#   File        :   tkoptions.py
#
#   Author      :   GeeHB
#
#   Description :   Options specific to GUI
#

from options import APP_SHORT_NAME

# GUI
TK_TITLE = f"tk{APP_SHORT_NAME}"
TK_WIN_WITH = 300
TK_WIN_HEIGHT = 400

# Texts ...
TK_BROWSE           = "Browse"
TK_BROWSE_PREV      = "<<"
TK_BROWSE_NEXT      = ">>"

TK_CHOOSE_FOLDER    = "Choose grids'folder"
TK_EDIT             = "Edit"
TK_FILENAME         = "File name"
TK_FOLDERNAME       = "Folder name"
TK_GRID_EDITION     = "Grid edition"
TK_GRID_FOLDER      = "Grid folder"
TK_NEW              = "New"
TK_NEW_GRID         = "New grid"
TK_OBVIOUS_VALUES   = "Obvious values"
TK_REVERT           = "Revert"
TK_SAVE             = "Save"
TK_SHOW_PROGRESS    = "Show progess"
TK_SOLUTION         = "Solution"
TK_SOLVE            = "Solve" 
TK_SOLVING          = "Solving"

TK_TAB_GRIDS        = "Grids"
TK_TAB_SOLVE        = TK_SOLVE


# Progression modes
#
TK_PROGRESS_NONE            = "none"
TK_PROGRESS_SLOW            = "slow"
TK_PROGRESS_SINGLETHREADED  = TK_PROGRESS_SLOW
TK_PROGRESS_MULTITHREADED   = "multithreaded"

# Types of new grids and count of empty elements
TK_NEW_EMPTY = "Empty"
TK_NEW_EASY = "Easy"
TK_NEW_MEDIUM = "Medium"
TK_NEW_HARD = "Hard"

#EOF