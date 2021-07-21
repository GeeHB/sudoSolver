#!/usr/bin/python3
#
# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   JHB
#
#   Description :   Display, edit and solve a sudoku grid
#
#   Version     :   1.2.4
#
#   Date        :   2021-07-21
#

import time
import options
from sudoku import sudoku
from drawThread import drawThread
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
    params.usage(False)
    
    # my sudoku grid
    solver = None

    # Loading ...
    #
    try:
        solver = sudoku(params.consoleMode_)
        
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

            # Start the drawing thread
            if params.drawProgress_:
                myThread = drawThread(solver.outputs(), solver.grid())
                myThread.start()
            else:
                solver.displayText("Solving ...", False)
      
            # Obvious values first ...
            count = 0
            if True == params.obviousValues_:
                count, obvDuration = solver.findObviousValues()

            # ... and then try to resolve
            attempts, duration = solver.resolve()

            # Stop the drawing thread
            if params.drawProgress_:
                myThread.stop()
            
            # Display the solution
            solver.showGrid()   
            solver.displayText("Press a key to quit", False)

            time.sleep(1)

            solver.waitForKeyDown()
            solver.close()

            # A few stats.
            #
            print("\t- " + solver.fileName())

            # Found obvious values ?
            if count:
                print("\t- Found " + str(count) + " obvious value(s) in " + str(round(obvDuration, 2)) + " second(s)")
            else:
                print("\t- No obvious value found")

            print("\t- Solved in " + str(round(duration, 2)) + " second(s)")
            print("\t- " + str(attempts) + " attempt(s)\n") 

            # Export the solution ?
            if params.exportSoluce_:
                comments = []
                comments.append(" ")
                comments.append(" Source file : " + solver.fileName())
                comments.append(" ")
                comments.append("Solved by JHB::sudoSolver.py in " + str(round(duration, 2)) + " sec.")
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