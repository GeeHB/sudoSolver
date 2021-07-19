#!/usr/bin/env python3

# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   JHB
#
#   Description :   Display, edit and solve a sudoku grid
#
#   Version     :   1.1.2
#
#   Date        :   2021-07-19
#

import time
from options import options
from colorizer import colorizer, backColor, textColor, textAttribute
from sudoku import sudoku
from ownExceptions import sudokuError

CURRENT_VERSION = "1.1.2"

#
#   Functions
#

if __name__ == '__main__':

    # Parse command line
    #
    params = options()
    if False == params.parse() :
        exit(1)

    # Let's start the game
    print(params.color_.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]), "- version", CURRENT_VERSION)

    # my sudoku grid
    solver = None

    # Loading ...
    #
    try:
        solver = sudoku(params.drawFreq_, params.consoleMode_)
        
        if params.browseFolder_:
            if not solver.allowFolderBrowsing():
                solver.close()
                raise sudokuError("This display mode is not compatible with folder browsing")
            params.fileName_ = solver.browse(params.folderName_)
            if 0 == len(params.fileName_):
                # Cancelled by user
                exit(0)
        else :
            solver.load(params.fileName_, False == params.editMode_)
    except sudokuError as e:
        print(e)
        exit(1)
    except IndexError:
        print("Too many lines in the file")
        exit(1)
    except:
        print("Unknown error while loading '" + params.fileName_ + "'")
        exit(1)
        
    # Edition and/or resolution
    #
    try:
        # display starting grid
        solver.showGrid()

        # Edition
        if params.editMode_:
            if False == solver.allowEdition():
                solver.close()
                solver.displayText("This display mode is not compatible with grid edition")
                exit(1)

            # Succefully edited ?
            if False == solver.edit():
                solveMode = False
        
        # Search for the solution
        if params.solveMode_:       
            if False == params.editMode_:
                solver.displayText("Press a key to start resolution", False)
                solver.waitForKeyDown()

            solver.displayText("Solving ...", False)
                  
            # Obvious values first ...
            if True == params.obviousValues_:
                count, duration = solver.findObviousValues()
                
                # Found obvious values ?
                if count:
                    print("Found " + str(count) + " obvious value(s) in " + str(duration) + " second(s)")
                else:
                    print("No obvious value found")

            # ... and then try to resolve
            attempts, duration = solver.resolve()
            
            # Display the solution
            solver.showGrid()   
            solver.displayText("Press a key to quit", False)

            time.sleep(1)

            solver.waitForKeyDown()
            solver.close()

            # A few stats.
            print("Resolution duration : " + str(duration) + " second(s)")
            print("Attempts : " + str(attempts)) 

            # Export the solution ?
            if params.exportSoluce_:
                comments = []
                comments.append(" ")
                comments.append(" Source file : " + solver.fileName())
                comments.append(" ")
                comments.append("Solved by JHB::sudoSolver.py in " + str(duration) + " sec.")
                comments.append(" ")
                if True == solver.save(True, comments):
                    print("Soluce successfully saved in ", solver.fileName() + solver.FILE_EXPORT_EXTENSION) 

    except sudokuError as e:
        print(e)
    except IndexError:
        print("No soluce found for this grid")
    except:
        print("Unknown error")

# EOF