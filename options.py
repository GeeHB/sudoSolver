# coding=UTF-8
#
#   File        :   options.py
#
#   Author      :   GeeHB
#
#   Description :   Handle command-line & shared consts.
#

import sysconfig, argparse
from sharedTools import colorizer as color

# App informations
APP_NAME = "sudoSolver.py"
APP_CURRENT_VERSION = "1.6.1"
APP_RELEASE_DATE = "06/14/2023"
APP_AUTHOR = "GeeHB (j.henrybarnaudiere@gmail.com)"

# Command line options
#

ARG_BROWSE_S = "-b"                 # Browse a folder
ARG_BROWSE   = "--browse"
COMMENT_BROWSE = "Browse the {FOLDER} folder and display contained grids"

ARG_EDIT_S = "-e"                   # Edit (and modify or create) a grid
ARG_EDIT   = "--edit"
COMMENT_EDIT = "Edit or create the {FILE} file"

ARG_SOLVE_S = "-s"                  # Search for a solution for the grid
ARG_SOLVE   = "--solve"
COMMENT_SOLVE = "Solve (find a solution) for the grid saved in {FILE} file"

ARG_BROWSE_AND_SOLVE_S = "-bs"
ARG_BROWSE_AND_SOLVE = "--browseSolve"
COMMENT_BROWSE_AND_SOLVE = "Browse the {FOLDER} folder and solve the choosen grid"

ARG_EDIT_AND_SOLVE_S = "-es"
ARG_EDIT_AND_SOLVE = "--editSolve"
COMMENT_EDIT_AND_SOLVE = "Edit and solve the sudoku in the {FILE} file"

ARG_SEARCH_OBVIOUS_S = "-o"         # Search for obvious values
ARG_SEARCH_OBVIOUS = "--obvious"
COMMENT_SEARCH_OBVIOUS = "Search obvious vals before brute-force solution searching"

ARG_SAVE_SOLUTION_S = "-x"          # Save / export the solution
ARG_SAVE_SOLUTION = "--export"
COMMENT_SAVE_SOLUTION = "Save the solution of the grid"

ARG_CONSOLE_S = "-c"                # Console mode
ARG_CONSOLE = "--console"
COMMENT_CONSOLE = "Force displays in console mode (using nCurses if available)"

# Show grid during the search process
ARG_DETAILS_S = "-d"           # Draw details
ARG_DETAILS = "--details"
COMMENT_DETAILS = "Show grids during proces"
MIN_DETAILS    = 1 # Slow
MAX_DETAILS    = 2

#
#   options object : command-line parsing and parameters management
#
class options(object):

    # Construction
    #
    def __init__(self):

        # Default values
        self.color_ = color.colorizer(True, False)
        self.consoleMode_ = False
        self.browseFolder_ = False
        self.editMode_ = False
        self.solveMode_ = False
        self.fileName_ = ""
        self.folderName_ = ""
        self.exportSolution_ = False
        self.obviousValues_ = False             # don't search "obvious" values before trying to solve
        self.multiThreadedProgress_ = False     # Draw the grid during the search process
        self.singleThreadedProgress_ = False    # Draw "slowly" the grid during search process

    # Browse the command line
    #   returns True when ok
    def parse(self):

        parser = argparse.ArgumentParser(epilog = self.version())

        # Define parameters
        #
         
        # Console display mode ?
        parser.add_argument(ARG_CONSOLE_S, ARG_CONSOLE, action='store_true', help = COMMENT_CONSOLE, required = False)
        
        # Export the solution ?
        parser.add_argument(ARG_SAVE_SOLUTION_S, ARG_SAVE_SOLUTION, action='store_true', help = COMMENT_SAVE_SOLUTION, required = False)
        
        # Search obvious values ?
        parser.add_argument(ARG_SEARCH_OBVIOUS_S, ARG_SEARCH_OBVIOUS, action='store_true', help = COMMENT_SEARCH_OBVIOUS, required = False)
        
        # display progression?
        parser.add_argument(ARG_DETAILS_S, ARG_DETAILS, help = COMMENT_DETAILS, required = False, nargs=1, type=int, choices=range(MIN_DETAILS, MAX_DETAILS + 1))
        
        # Mutually exclusive actions
        #
        action = parser.add_mutually_exclusive_group()

        # Browse folder
        action.add_argument(ARG_BROWSE_S, ARG_BROWSE, help = COMMENT_BROWSE, metavar = "FOLDER", required = False, nargs=1)

        # Edition file
        action.add_argument(ARG_EDIT_S, ARG_EDIT, help = COMMENT_EDIT, metavar = "FILE", required = False, nargs=1) 
        
        # Solve file
        action.add_argument(ARG_SOLVE_S, ARG_SOLVE, help = COMMENT_SOLVE, metavar = "FILE", required = False, nargs=1)

        # Browse folder and edit selected file
        action.add_argument(ARG_BROWSE_AND_SOLVE_S, ARG_BROWSE_AND_SOLVE, help = COMMENT_BROWSE_AND_SOLVE, metavar = "FOLDER", required = False, nargs=1)

        # Edit and solve file
        action.add_argument(ARG_EDIT_AND_SOLVE_S, ARG_EDIT_AND_SOLVE, help = COMMENT_EDIT_AND_SOLVE, metavar = "FILE", required = False, nargs=1)
        
        
        # Parse line
        #
        args = parser.parse_args()

        # Console mode
        self.consoleMode_ = args.console

        # Export / save the solution
        self.exportSolution_ = args.export

        # Search obvious values ?
        self.obviousValues_ = args.obvious

        # Solve ?
        if args.solve is not None:
            self.fileName_ = args.solve[0]
            self.solveMode_ = True
        else:
            # Edition mode ?
            if args.edit is not None:
                self.fileName_ = args.edit[0]
                self.editMode_ = True                
            else:
                # Edit and solve
                if args.editSolve is not None:
                    self.fileName_ = args.editSolve[0]
                    self.editMode_ = True
                    self.solveMode_ = True                    
                else:
                    # Parse/browse folder ?
                    if args.browse is not None:
                        self.folderName_ = args.browse[0]
                        self.browseFolder_ = True
                        self.editMode_ = True                        
                    else:
                        # browse and solve ?
                        if args.browseSolve is not None:
                            self.folderName_ = args.browseSolve[0]
                            self.browseFolder_ = True
                            self.editMode_ = True
                            self.solveMode_ = True
        
        # display grid ?
        display = args.details if args.details is not None else 0 
        
        if display == 2:
            self.multiThreadedProgress_ = True
            # Check if macOS
            if -1 != sysconfig.get_platform().find("macos"):
                print("No multi-threading on macos")
                self.multiThreadedProgress_ = False
                self.singleThreadedProgress_ = True
            else:
                self.singleThreadedProgress_ = False
        else :
            self.singleThreadedProgress_ = True if display == 1 else False

        # Export solution => solverMode should be activated
        if self.exportSolution_ and not self.solveMode_:
            return False
        
        # At least one action !
        ret = True if self.editMode_ or self.solveMode_ or self.browseFolder_ else False
        if not ret :
            parser.print_help()
            return False
        
        return True

    # Display app version infos
    #
    #   return a string
    #
    def version(self, verbose = True):
        if None == self.color_:
            self.color_ = color.colorizer(True)

        return f"{self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD], datePrefix=(False == verbose))} by {APP_AUTHOR} - release {APP_CURRENT_VERSION} - {APP_RELEASE_DATE}"
# EOF