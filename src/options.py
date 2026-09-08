# coding=UTF-8
#
#   File        :   options.py
#
#   Author      :   GeeHB
#
#   Description :   Handle command-line & shared consts.
#

import argparse
import sysconfig

from sharedTools import colorizer as color
from sharedTools import statusbits

# App informations
APP_SHORT_NAME = "sudoSolver"
APP_NAME = f"{APP_SHORT_NAME}.py"
APP_CURRENT_VERSION = "3.1.4"
APP_RELEASE_DATE = "05/08/2026"
APP_AUTHOR_SHORT = "GeeHB"
APP_AUTHOR = f"{APP_AUTHOR_SHORT} (j.henrybarnaudiere@gmail.com)"

# Expected minnimal version of Python
#
PYTHON_VER_MAJ = 3
PYTHON_VER_MIN = 10

# Command line options
#

ARG_BROWSE_S = "-b"  # Browse a folder
ARG_BROWSE = "--browse"
COMMENT_BROWSE = "Browse the {FOLDER} folder and display contained grids"

ARG_EDIT_S = "-e"  # Edit (and modify or create) a grid
ARG_EDIT = "--edit"
COMMENT_EDIT = "Edit or create the {FILE} file"

ARG_SOLVE_S = "-s"  # Search for a solution for the grid
ARG_SOLVE = "--solve"
COMMENT_SOLVE = "Solve (find a solution) for the grid saved in {FILE} file"

ARG_USER_S = "-u"  # Search for a solution for the grid
ARG_USER = "--user"
COMMENT_USER = "User mode"

ARG_BROWSE_AND_SOLVE_S = "-bs"
ARG_BROWSE_AND_SOLVE = "--browseSolve"
COMMENT_BROWSE_AND_SOLVE = "Browse the {FOLDER} folder and solve the choosen grid"

FILE_EXPORT_EXTENSION = ".solution"  # A solution grid file

ARG_EDIT_AND_SOLVE_S = "-es"
ARG_EDIT_AND_SOLVE = "--editSolve"
COMMENT_EDIT_AND_SOLVE = "Edit and solve the sudoku in the {FILE} file"

ARG_NEW_S = "-n"  # New grid
ARG_NEW = "--new"
COMMENT_NEW = "Create a new grid of {COMPLEXITY} complexity"

ARG_SEARCH_OBVIOUS_S = "-o"  # Search for obvious values
ARG_SEARCH_OBVIOUS = "--obvious"
COMMENT_SEARCH_OBVIOUS = "Search obvious vals before brute-force solution searching"

ARG_SAVE_SOLUTION_S = "-x"  # Save / export the solution
ARG_SAVE_SOLUTION = "--export"
COMMENT_SAVE_SOLUTION = "Save the solution of the grid"

# Show grid during the search process
ARG_DETAILS_S = "-d"  # Draw details
ARG_DETAILS = "--details"
COMMENT_DETAILS = "Show grids during process"

#
# App. folders
#
DEF_GRID_FOLDER = "../grids"
DEF_ASSETS_FOLDER = "../assets"

#
#   options object : command-line parsing and parameters management
#
class options:
    # Progression modes
    PROGRESS_NONE:int = 0  # Don't show progession
    PROGRESS_SLOW:int = 1  # Singlethreaded mode
    PROGRESS_SINGLETHREADED:int = PROGRESS_SLOW
    PROGRESS_SPEED:int = 2  # Use a distinct thread for displaying grids
    PROGRESS_MULTITHREADED:int = PROGRESS_SPEED

    # Exec modes
    EXEC_NONE:int = statusbits.STATUS_NONE
    EXEC_CREATE:int = 1
    EXEC_EDIT:int = EXEC_CREATE
    EXEC_USER:int = 2
    EXEC_SOLVE:int = 4

    # Types of new grids and count of empty elements
    NEW_EMPTY:str = "Empty"
    NEW_EASY:str = "Easy"
    NEW_MEDIUM:str = "Medium"
    NEW_HARD:str = "Hard"

    # Grid complexity - ie. count of filled elements
    COMPLEXITY_EMPTY:int = 0
    COMPLEXITY_EASY:int = 33
    COMPLEXITY_MEDIUM:int = 26
    COMPLEXITY_HARD:int = 22

    # Construction
    #
    def __init__(self):
        # Default values
        self.color_:color.colorizer = color.colorizer(True, False)
        self.browseFolder_:bool = False
        self.fileName_:str = ""
        self.folderName_:str = ""
        self.exportSolution_:bool = False
        self.obviousValues_:bool = False
        self.progressMode_:int = self.PROGRESS_NONE
        self.execMode_:statusbits.statusBits = statusbits.statusBits(self.EXEC_NONE)
        self.newGrid_:int = self.COMPLEXITY_EMPTY
        self.userMode_:bool = False

    # Browse the command line
    #   returns True when ok
    def parse(self):
        parser = argparse.ArgumentParser(epilog=self.version())

        # User mode
        _ = parser.add_argument(
            ARG_USER_S, ARG_USER, action="store_true", help=COMMENT_USER, required=False
        )

        # Export the solution ?
        _ = parser.add_argument(
            ARG_SAVE_SOLUTION_S,
            ARG_SAVE_SOLUTION,
            action="store_true",
            help=COMMENT_SAVE_SOLUTION,
            required=False,
        )

        # Search obvious values ?
        _ = parser.add_argument(
            ARG_SEARCH_OBVIOUS_S,
            ARG_SEARCH_OBVIOUS,
            action="store_true",
            help=COMMENT_SEARCH_OBVIOUS,
            required=False,
        )

        # display progression?
        _ = parser.add_argument(
            ARG_DETAILS_S,
            ARG_DETAILS,
            help=COMMENT_DETAILS,
            required=False,
            nargs=1,
            type=int,
            choices=range(self.PROGRESS_SLOW, self.PROGRESS_SPEED + 1),
        )

        # Mutually exclusive actions
        #
        action = parser.add_mutually_exclusive_group()

        # Browse folder
        _ = action.add_argument(
            ARG_BROWSE_S,
            ARG_BROWSE,
            help=COMMENT_BROWSE,
            metavar="FOLDER",
            required=False,
            nargs=1,
        )

        # Edition file
        _ = action.add_argument(
            ARG_EDIT_S,
            ARG_EDIT,
            help=COMMENT_EDIT,
            metavar="FILE",
            required=False,
            nargs=1,
        )

        # Solve file
        _ = action.add_argument(
            ARG_SOLVE_S,
            ARG_SOLVE,
            help=COMMENT_SOLVE,
            metavar="FILE",
            required=False,
            nargs=1,
        )

        # Browse folder and edit selected file
        _ = action.add_argument(
            ARG_BROWSE_AND_SOLVE_S,
            ARG_BROWSE_AND_SOLVE,
            help=COMMENT_BROWSE_AND_SOLVE,
            metavar="FOLDER",
            required=False,
            nargs=1,
        )

        # Edit and solve file
        _ = action.add_argument(
            ARG_EDIT_AND_SOLVE_S,
            ARG_EDIT_AND_SOLVE,
            help=COMMENT_EDIT_AND_SOLVE,
            metavar="FILE",
            required=False,
            nargs=1,
        )

        # Create a new grid
        _ = action.add_argument(
            ARG_NEW_S,
            ARG_NEW,
            help=COMMENT_NEW,
            metavar="COMPLEXITY",
            choices=[self.NEW_EMPTY, self.NEW_EASY, self.NEW_MEDIUM, self.NEW_HARD],
            required=False,
        )

        # Parse line
        #
        args = parser.parse_args()

        # User mode ?
        self.userMode_ = args.user  # pyright: ignore[reportAny]

        # Export / save the solution
        self.exportSolution_ = args.export

        # Search obvious values ?
        self.obviousValues_ = args.obvious

        # Solve ?
        if args.solve is not None:
            self.fileName_ = args.solve[0]
            self.execMode_.set(self.EXEC_SOLVE)
        else:
            # Edition mode ?
            if args.edit is not None or args.editSolve is not None:
                self.fileName_ = (
                    args.edit[0] if args.edit is not None else args.editSolve[0]
                )
                self.execMode_.set(
                    self.EXEC_EDIT | self.EXEC_SOLVE
                    if args.editSolve is not None
                    else 0
                )
            else:
                # Parse/browse folder ?
                if args.browse is not None or args.browseSolve is not None:
                    self.folderName_ = (
                        args.browse[0]
                        if args.browse is not None
                        else args.browseSolve[0]
                    )
                    self.browseFolder_ = True
                    self.execMode_.set(
                        self.EXEC_EDIT | self.EXEC_SOLVE
                        if args.browseSolve is not None
                        else 0
                    )

        if self.userMode_ == False and args.editSolve is not None:
            self.execMode_.set(self.EXEC_SOLVE)

        # Generate a new grid ?
        # if True == self.editMode_ :
        if self.execMode_.isSet(self.EXEC_EDIT) and args.new is not None:
            mode : str = args.new[0]
            match mode:
                case self.NEW_MEDIUM:
                    self.newGrid_ = self.COMPLEXITY_MEDIUM
                case self.NEW_HARD:
                    self.newGrid_ = self.COMPLEXITY_HARD
                case self.NEW_EASY:
                    self.newGrid_ = self.COMPLEXITY_EASY
                case _:
                    self.newGrid_ = self.COMPLEXITY_EASY

        # Display grid during the search process ?
        display = args.details[0] if args.details is not None else 0
        if display == 2:
            self.progressMode_ = self.PROGRESS_MULTITHREADED
            # Check if macOS
            if -1 != sysconfig.get_platform().find("macos"):
                print("No multi-threading on macos")
                self.progressMode_ = self.PROGRESS_SINGLETHREADED
        else:
            self.progressMode_ = (
                self.PROGRESS_SINGLETHREADED if display == 1 else self.PROGRESS_NONE
            )

        # Export solution => solverMode should be activated
        if self.exportSolution_ and not self.execMode_.isSet(self.EXEC_SOLVE):
            return False

        # At least one action !
        ret = bool(
            self.execMode_.isSet(self.EXEC_EDIT)
            or self.execMode_.isSet(self.EXEC_SOLVE)
            or self.browseFolder_
        )
        if not ret:
            parser.print_help()
            return False

        return True

    # Display app version infos
    #
    #   return a string
    #
    def version(self)->str:
        self.color_ = color.colorizer(True)
        return f"{self.color_.colored(APP_NAME, formatAttr=[color.textAttribute.BOLD])} by {APP_AUTHOR} - release {APP_CURRENT_VERSION} - {APP_RELEASE_DATE}"


#
# stats - Informations about a solution
#
class stats:
    def __init__(self) -> None:
        self.obvValues_ : int = 0          # Count of obvious values found
        self.obvDuration_ : float = 0.0      # Duration in sec. of obvious-values search process
        self.bruteDuration_ : float = 0.0    # Duration in sec. of brute-force search process
        self.bruteAttempts_ : int  = 0     # Brute-force attempts counter

# EOF
