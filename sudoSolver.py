#!/usr/bin/python3
#
# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   GeeHB
#
#   Description :   Display, edit and solve a sudoku grid
#

import time
import options, outputs
from sudoku import sudoku
from ownExceptions import sudokuError

#
#   Functions
#

if '__main__' == __name__:

    # Parse command line
    #
    params = options.options()
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
        solver = sudoku(params.consoleMode_, params.singleThreadedProgress_, params.multiThreadedProgress_)
        
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
        print("Too many lines in the file")
        exitNow = True
    except:
        print("Unknown error while loading '" + params.fileName_ + "'")
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
        solver.showGrid()

        # Edition
        if params.editMode_:
            # Succefully edited ?
            if False == solver.edit():
                solveMode = False
        
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
                    solver.displayText("Found " + str(myStats.obvValues_) + " obvious values", False)
                    solver.showGrid()   
                    solver.waitForKeyDown()
                    
            # ... and then try to resolve
            found, escaped, myStats.bruteAttempts_, myStats.bruteDuration_ = solver.resolve(params.multiThreadedProgress_)

            # Display the solution (if any)
            solver.showGrid()   
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
                    comments.append(" Source file : " + params.fileName_)
                    comments.append(" ")
                    comments.append("Solved by GeeHB::sudoSolver.py in " + str(round(myStats.bruteDuration_, 2)) + " sec.")
                    comments.append(" ")
                    
                    if True == solver.save(True, comments):
                        print("Solution successfully saved in ", params.fileName_ + solver.FILE_EXPORT_EXTENSION) 

            solver.close()
            
            # A few stats.
            if True == found:
                solver.showStats(params, myStats)
            else:
                print("No solution found for '" + params.fileName_ + "'")

    except sudokuError as e:
        # Other error
        print(e)    
    """
    except:
        print("Unknown error")
    """
# EOF