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
APP_RELEASE_DATE = "12 jun. 2023"
APP_AUTHOR = "GeeHB (j.henrybarnaudiere@gmail.com)"

# Command line options
#

ARG_BROWSE_S = "-b"                 # Browse a folder
ARG_BROWSE   = "--browse"
COMMENT_BROWS = "Browse the folder and display contained grids"

ARG_EDIT_S = "-e"                   # Edit (and modify or create) a grid
ARG_EDIT   = "--edit"
COMMENT_EDIT = "Edit or create the file"

ARG_SOLVE_S = "-s"                  # Search for a solution for the grid
ARG_SOLVE   = "--solve"
COMMENT_SOLVE = "Solve (find a solution) for the grid"

ARG_BROWSE_AND_SOLVE_S = "-bs"
COMMENT_BROWSE_AND_SOLVE = "Browse the folder and solve the choosen grid"

ARG_EDIT_AND_SOLVE_S = "-es"
COMMENT_EDIT_AND_SOLVE = "Edit and solve the sudoku"

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
MIN__DETAILS    = 1 # Slow
MAX_DTAILS      = 2

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
        self.obviousValues = False              # don't search "obvious" values before trying to solve
        self.multiThreadedProgress_ = False     # Draw the grid during the search process
        self.singleThreadedProgress_ = False    # Draw "slowly" the grid during search process

    # Browse the command line
    #   returns True when ok
    def parse(self):
        if False == self._parse():
            self.usage()
            return False
        return True

    def _parse(self):

        parameters = parser.cmdLineParser(ARG_OPTION_CHAR)
        
        # Parameters needed
        if 0 == parameters.size():
            return False
        
        # Console display mode ?
        self.consoleMode_ = not (parameters.findAndRemoveOption(ARG_OPTION_CONSOLE) == parameters.NO_INDEX)

        # Export the solution ?
        self.exportSolution_ = not (parameters.findAndRemoveOption(ARG_OPTION_SAVE_SOLUTION) == parameters.NO_INDEX)

        # Search obvious values ?
        self.obviousValues_ = not (parameters.findAndRemoveOption(ARG_OPTION_SEARCH_OBVIOUS) == parameters.NO_INDEX)

        # Solve mode ?
        rets = parameters.getOptionValue(ARG_OPTION_SOLVE)
        if False == rets[1] and rets[0] != None:
            # File name expected
            self.fileName_ = rets[0]
            self.solveMode_ = True
        else:
            # Edition mode ?
            rets = parameters.getOptionValue(ARG_OPTION_EDIT)
            if False == rets[1] and rets[0] != None:
                self.fileName_ = rets[0]
                self.editMode_ = True                
            else:
                # Edition & resolution ?
                rets = parameters.getOptionValue(ARG_OPTION_EDIT_AND_SOLVE)
                if False == rets[1] and rets[0] != None:
                    self.fileName_ = rets[0]
                    self.editMode_ = True
                    self.solveMode_ = True                    
                else:
                    # Parse/browse folder ?
                    rets = parameters.getOptionValue(ARG_OPTION_BROWSE)
                    if False == rets[1] and rets[0] != None:
                        self.folderName_ = rets[0]
                        self.browseFolder_ = True
                        self.editMode_ = True                        
                    else:
                        # browse and solve ?
                        rets = parameters.getOptionValue(ARG_OPTION_BROWSE_AND_SOLVE)
                        if not rets is None and False == rets[1] and rets[0] != None:
                            self.folderName_ = rets[0]
                            self.browseFolder_ = True
                            self.editMode_ = True
                            self.solveMode_ = True
                        else:
                            showUsage = True
        
        # display progression?
        self.singleThreadedProgress_ = not (parameters.NO_INDEX == parameters.findAndRemoveOption(ARG_OPTION_SHOW_DETAILS))
        
        # display grid in multithreaded mode ?
        self.multiThreadedProgress_ = not (parameters.NO_INDEX == parameters.findAndRemoveOption(ARG_OPTION_SHOW_DETAILS_MT))
        if True == self.multiThreadedProgress_:
            # Check if macOS
            if -1 != sysconfig.get_platform().find("macos"):
                print("No multi-threading on macos")
                self.multiThreadedProgress_ = False
                self.singleThreadedProgress_ = True
            else:
                self.singleThreadedProgress_ = False

        # Export solution => solverMode should be activated
        if self.exportSolution_ and not self.solveMode_:
            return False

        # There should be no options left and no errors ...
        if parameters.options() > 0 or (0 == len(self.fileName_) and 0 == len(self.folderName_)):
            return False
        
        # Done
        return True

    # Display app version infos
    #
    #   return a string
    #
    def version(self):
        if None == self.color_:
            self.color_ = color.colorizer(True)

        return f"{self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD], datePrefix=(False == self.verbose_))} by {APP_AUTHOR} - release {APP_CURRENT_VERSION} - {APP_RELEASE_DATE}"
# EOF