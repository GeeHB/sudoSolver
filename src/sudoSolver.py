#!/usr/bin/env python
#
#
# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   GeeHB
#
#   Description :   Display, edit and solve sudokus

#                   Command line version
#

import sys
import time

from options import (
    APP_AUTHOR_SHORT,
    APP_NAME,
    FILE_EXPORT_EXTENSION,
    PYTHON_VER_MAJ,
    PYTHON_VER_MIN,
    options,
    stats,
)

# from gridMaker import gridMaker
from ownExceptions import sudokuError
from sudoku import sudoku

#
#   Functions
#


# Create the solver
#
def _create():
    solver = None
    exitNow = False

    try:
        solver = sudoku(params.progressMode_)
        if params.browseFolder_:
            if not solver.allowFolderBrowsing():
                solver.close()
                raise sudokuError(
                    "This display mode is not compatible with folder browsing"
                )

            params.fileName_ = solver.browse(params.folderName_)
            if 0 == len(params.fileName_):
                # Cancelled by user
                exitNow = True

            """
            # Generate a new grid
            maker = gridMaker(grid = solver)
            maker.newGrid()
            maker.removeElements(options.COMPLEXITY_HARD)

            solver.displayGrid()
            """
        else:
            solver.load(
                params.fileName_, False == params.execMode_.isSet(options.EXEC_EDIT)
            )
    except sudokuError as e:
        print(e)
        exitNow = True
    except IndexError:
        print("Too many lines in the file", file=sys.stderr)
        exitNow = True
    except KeyboardInterrupt:
        print("Canceled by user")
        exitNow = True
        # except Exception as e:
        # print(f"Unknown error : {str(e)}", file=sys.stderr)
        # exitNow = True

    return solver, exitNow


# Start the solver/editor
#
def _sudoku(solver : sudoku):
    # Edition and/or resolution
    #
    try:
        # Display starting grid
        solver.displayGrid()

        # Edition
        if params.execMode_.isSet(options.EXEC_EDIT):
            # Succefully edited ?
            escape, saved = solver.edit()
            if escape == True or saved == False:
                # Escaped or error while saving
                params.execMode_.remove(options.EXEC_SOLVE)

        # Search for the solution
        #
        myStats = stats()
        if params.execMode_.isSet(options.EXEC_SOLVE):
            if False == params.execMode_.isSet(options.EXEC_EDIT):
                solver.displayText("Press a key to start the solver", False)
                solver.waitForKeyDown()

            # Obvious values first ...
            if True == params.obviousValues_:
                myStats.obvValues_, myStats.obvDuration_ = solver.findObviousValues()

                if myStats.obvValues_ > 0:
                    solver.displayText(
                        f"Found {myStats.obvValues_!r} obvious values", False
                    )
                    solver.displayGrid()
                    solver.waitForKeyDown()

            # ... and then try to resolve
            found, escaped, myStats.bruteAttempts_, myStats.bruteDuration_ = (
                solver.resolve()
            )

            # Display the solution (if any)
            solver.displayGrid()
            solver.displayText("Press a key to quit", False)

            time.sleep(1)

            solver.waitForKeyDown()

            if escaped:
                print("Resolution process canceled")
            else:
                # Export the solution ?
                if params.exportSolution_:
                    comments : list[str] = []
                    comments.append(" ")
                    comments.append(f" Source file : {params.fileName_}")
                    comments.append(" ")
                    comments.append(
                        f"Solved by {APP_AUTHOR_SHORT}::{APP_NAME} in {round(myStats.bruteDuration_, 2)!r} sec."
                    )
                    comments.append(" ")

                    if solver.save(True, comments) is not None:
                        print(
                            f"Solution successfully saved in {params.fileName_}{FILE_EXPORT_EXTENSION}"
                        )

            solver.close()

            # A few stats.
            if True == found:
                solver.showStats(params, myStats)
            else:
                print(f"No solution found for '{params.fileName_}'")
    except sudokuError as e:
        # Other error
        print(e)
    # except:
    #   print("Unknown error", file=sys.stderr)

# Entry point
if "__main__" == __name__:
    # Check python ver.
    #
    ver = sys.version_info
    if (
        ver.major < PYTHON_VER_MAJ
        or ver.major == PYTHON_VER_MAJ
        and ver.minor < PYTHON_VER_MIN
    ):
        print(
            f"Invalid python version. Expected min. release {PYTHON_VER_MAJ}.{PYTHON_VER_MIN}"
        )
        sys.exit(2)

    # Parse command line
    #
    params = options()
    if not params.parse():
        sys.exit(1)

    # Let's start the game
    print(params.version())

    # Loading ...
    #
    solver, exitNow = _create()

    # Exit anyway ...
    if True == exitNow or solver is None:
        if solver is not None:
            solver.close()
            del solver
        sys.exit(0)

    if not params.execMode_.isSet(options.EXEC_EDIT) and False == solver.allowEdition():
        solver.displayText("This display mode is not compatible with grid edition")
        solver.close()
        sys.exit(1)

    # ... action
    _sudoku(solver)

# EOF
