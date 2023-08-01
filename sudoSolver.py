#!/usr/bin/python3
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

import sys, time
from options import options, APP_AUTHOR_SHORT, APP_NAME, FILE_EXPORT_EXTENSION
import outputs
from sudoku import sudoku
from ownExceptions import sudokuError

#
#   Functions
#

if '__main__' == __name__:

    # Parse command line
    #
    params = options()
    if False == params.parse() :
        exit(1)

    # Let's start the game
    params.version()
    
    # my sudoku grid
    solver = None
    exitNow = False

    # Loading ...
    #
    try:
        solver = sudoku(params.consoleMode_, params.progressMode_)
        
        if params.browseFolder_:
            if not solver.allowFolderBrowsing():
                solver.close()
                raise sudokuError("This display mode is not compatible with folder browsing")
            params.fileName_ = solver.browse(params.folderName_)
            if 0 == len(params.fileName_):
                # Cancelled by user
                exitNow = True
        else :
            solver.load(params.fileName_, False == params.editMode_)
    except sudokuError as e:
        print(e)
        exitNow = True
    except IndexError:
        print("Too many lines in the file", file=sys.stderr)
        exitNow = True
    except KeyboardInterrupt as kbe:
        print("Canceled by user")
        exitNow = True
    except Exception as e:
        print(f"Unknown error : {str(e)}", file=sys.stderr)    
        exitNow = True
    
    # Exit anyway ...
    if True == exitNow :
        if solver is not None:
            solver.close()
        exit(0)
    
    # Edition and/or resolution
    #
    
    if params.editMode_ and False == solver.allowEdition():
        solver.close()
        solver.displayText("This display mode is not compatible with grid edition")
        exit(1)
    
    try:
        # Display starting grid
        solver.displayGrid()

        # Edition
        if params.editMode_:
            # Succefully edited ?
            done = solver.edit()
            if done[0] == True or done[1] == False:
                # Escaped or error while saving 
                params.solveMode_ = False
        
        # Search for the solution
        #
        myStats = outputs.stats
        if params.solveMode_:       
            if False == params.editMode_:
                solver.displayText("Press a key to start the solver", False)
                solver.waitForKeyDown()

            # Obvious values first ...
            if True == params.obviousValues_:
                myStats.obvValues_, myStats.obvDuration_ = solver.findObviousValues()

                if True == solver.outputs().useGUI() and myStats.obvValues_ > 0:
                    solver.displayText(f"Found {str(myStats.obvValues_)} obvious values", False)
                    solver.displayGrid()   
                    solver.waitForKeyDown()
                    
            # ... and then try to resolve
            found, escaped, myStats.bruteAttempts_, myStats.bruteDuration_ = solver.resolve()

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
                    comments = []
                    comments.append(" ")
                    comments.append(f" Source file : {params.fileName_}")
                    comments.append(" ")
                    comments.append(f"Solved by {APP_AUTHOR_SHORT}::{APP_NAME} in {str(round(myStats.bruteDuration_, 2))} sec.")
                    comments.append(" ")
                    
                    if solver.save(True, comments) is not None:
                        print(f"Solution successfully saved in {params.fileName_}{FILE_EXPORT_EXTENSION}") 

            solver.close()
            
            # A few stats.
            if True == found:
                solver.showStats(params, myStats)
            else:
                print(f"No solution found for '{params.fileName_}'")

    except sudokuError as e:
        # Other error
        print(e, file=sys.stderr)    
    """
    except:
        print("Unknown error", file=sys.stderr)
    """
# EOF