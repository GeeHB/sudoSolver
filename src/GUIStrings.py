# coding=UTF-8
#
#   File        :   GUIStrings.py
#
#   Author      :   GeeHB
#
#   Description :   Shared string consts
#
#

#
# Command line options
#

ARG_BROWSE_S = '-b'  # Browse a folder
ARG_BROWSE = '--browse'
COMMENT_BROWSE = 'Browse the {FOLDER} folder and display contained sudokus'

ARG_EDIT_S = '-e'  # Edit (and modify or create) a sudoku
ARG_EDIT = '--edit'
COMMENT_EDIT = 'Edit or create the {FILE} file'

ARG_SOLVE_S = '-s'  # Search a solution for the sudoku
ARG_SOLVE = '--solve'
COMMENT_SOLVE = 'Solve (find a solution) for the sudoku saved in {FILE} file'

ARG_BROWSE_AND_SOLVE_S = '-bs'
ARG_BROWSE_AND_SOLVE = '--browseSolve'
COMMENT_BROWSE_AND_SOLVE = 'Browse the {FOLDER} folder and solve the choosen sudoku'

ARG_EDIT_AND_SOLVE_S = '-es'
ARG_EDIT_AND_SOLVE = '--editSolve'
COMMENT_EDIT_AND_SOLVE = 'Edit and solve the sudoku in the {FILE} file'

ARG_SEARCH_OBVIOUS_S = '-o'  # Search for obvious values
ARG_SEARCH_OBVIOUS = '--obvious'
COMMENT_SEARCH_OBVIOUS = 'Search obvious vals before brute-force solution searching'

ARG_SAVE_SOLUTION_S = '-x'  # Save / export the solution
ARG_SAVE_SOLUTION = '--export'
COMMENT_SAVE_SOLUTION = 'Save the solution of the sudoku'

# Show sudoku during the search process
ARG_DETAILS_S = '-d'  # Draw details
ARG_DETAILS = '--details'
COMMENT_DETAILS = 'Show sudokus during the resolution process'

# Use wxPython library as GUI
ARG_WX_S = '-wx'
ARG_WX = '--wxPython'
COMMENT_WX = 'Use wkPython for drawings and GUI'

#
#  Files & folders
#

FOLDER_SUDOKUS = '../sudokus'
FOLDER_ASSETS = '../assets'

# File management
#
FILE_VALUE_SEPARATOR:str = ','  # Value separator in files
FILE_COMMENTS:str = '#'  # Comment lines start with
FILE_EXTENSION:str = '.txt'
FILE_EXPORT_EXTENSION:str = '.solution'  # A solution sudoku file

FILE_PARAMS_NAME:str='.sudoku_params.txt'   # app. parameters

FILE_TEMP_NAME:str='.sudoku_temp.txt'       # Temporary saved
FILE_TEMP_DETAILS_SEP:str = '-'

#
#  Message boxes
#
STR_CREATE:str = 'Sudoku creation'
STR_EXIT:str = 'Exiting app.'
STR_LOAD:str = 'Open sudoku'
STR_NEW:str = 'New sudoku'
STR_SAVE:str = 'Save sudoku'
STR_EDITION:str = 'Sudoku edition'
STR_EMPTY:str= 'empty'

STR_EDIT:str = 'Edit'
STR_EDIT_OR_SOLVE:str = 'Do you want to edit or to solve the current sudoku?'
STR_MODIFIED_ARRAY:str= 'The array has been modified. All modified elements will be turned into \'original\' elements.\nDo you want to proceed?'
STR_WILDCARD:str= 'Text Files (*.txt)|*.txt|All Files (*.*)|*.*'
STR_NOT_SAVED:str = 'Current content has not been saved.\nDo you want to proceed?'
STR_SAVE_SUCCESS:str= 'Current sudoku successfully saved as'

STR_SOLUTION:str = 'Solution'
STR_FOUND_SOLUTION:str = 'Congratulation.\n You find a solution for the array.'
STR_FOUND_A_SOLUTION:str = 'Found a solution'
STR_NO_SOLUTION:str = 'No solution found for this array'

STR_EMPTY_ARRAY:str = "The current sudoku array is empty."
STR_FINISHED_ARRAY:str = "The current sudoku is already completed."

STR_CANCEL_LOOSE_CHANGES:str = "All changes will be lost.\nDo you want to proceed?"

#
# Menus & toolbar items
#

# Display menu
STR_DISPLAY_MENU:str = 'Display'
STR_DISPLAY_CENTER:str = 'Center array'
STR_DISPLAY_HELP_MATRIX:str = 'Show help matrix'
STR_DISPLAY_HELP_COL_LINE:str = 'Show column and line'
STR_DISPLAY_HELP_NUMBER:str = 'Hightlight selected number'
STR_DISPLAY_THEMES:str = 'Themes'

# Creation menu
STR_CREATE_MENU:str = 'Create'
STR_CREATE_EMPTY:str = 'Empty'
STR_CREATE_EASY:str = 'Easy'
STR_CREATE_MEDIUM:str = 'Medium'
STR_CREATE_HARD:str = 'Hard'

STR_CREATE_UNDO:str = 'Undo'
STR_CREATE_MODIFY:str = 'Modify'
STR_CREATE_DONE:str = 'Done'
STR_CREATE_CANCEL:str = 'Cancel'

# Resolution
STR_SOLVE_SEARCH:str = 'Search for a solution'
STR_SOLVE_SEARCHING:str = 'Searching ...'
STR_SOLVE_NO_SOLUCE:str = 'This array is insolvable. \nYou should re-edit and modify it.'
STR_SOLVE_MENU:str = 'Solve'
STR_SOLVE_MANUAL:str = 'Manually'
STR_SOLVE_OBVIOUS:str = 'All obvious values'
STR_SOLVE_RESOLVE:str = 'Resolve'
STR_SOLVE_RESOLVE_SINGLE:str= 'Single thread'
STR_SOLVE_RESOLVE_MULTI:str= 'Multi-threaded'
STR_SOLVE_REVERT:str =  'Revert'

# Hypothesis and tags
STR_TIP_HYP_COMBO:str = 'List of colored hyptothesis'

STR_HYP_VALIDATE:str =  'Validate'
STR_TIP_HYP_VALIDATE:str = 'Validate current colored hyptothesis'

STR_HYP_REJECT:str =  'Reject'
STR_TIP_HYP_REJECT:str = 'Reject the current hyptothesis'

STR_EDIT_END:str =  STR_CREATE_DONE
STR_TIP_EDIT_END:str = 'End and validate edition'

STR_EDIT_CANCEL:str =  STR_CREATE_CANCEL
STR_TIP_EDIT_CANCEL:str = 'Cancel edition'

# Contextual menu
STR_POPUP_EMPTY:str = "Empty"

# Temp file
#
STR_TEMP_FILE:str = "Previous sudoku"
STR_TEMP_EXIST:str = "A stored sudoku exists on disk.\nDo you want to continue the resolution ?"

#
# Toolbar
#
STR_TOOLBAR:str = '---'
STR_MODE:str = 'mode'
STR_MODE_CREATION:str = 'Creation'
STR_MODE_RESOLUTION:str = 'Resolution'

STR_FILLED:str = 'Filled'


STR_TIP_HELP:str = 'Resolution helpers'

STR_HELP_CHOOSE:str = STR_TIP_HELP
STR_HELP_OBVIOUS_SINGLE:str = "Single obvious value"
STR_HELP_OBVIOUS_ALL:str = STR_SOLVE_OBVIOUS

STR_HELP_OFFER:str = 'Offer a value'
STR_HELP_ERROR:str = 'Show an error'
STR_HELP_ERRORS:str = 'Error count'

STR_HELP_NO_OBVIOUS:str = 'No obvious value found.'
STR_HELP_ARRAY_FULL:str = 'The array is already full.\nNo value value will be offered.'
STR_HELP_NO_ERROR:str = 'There is no error in the current array.'
STR_HELP_FOUND_ERRORS:str = 'errors were found.'

#
# Errors
#

STR_ERROR_INVALID_PYTHON_VER:str = "Invalid python version. Expected min. release"

# EOF
