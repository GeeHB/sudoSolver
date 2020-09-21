#!/usr/bin/env python3

# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   JHB
#
#   Description :   Display and solve a sudoku grid
#
#   Version     :   0.1.26
#
#   Date        :   2020-09-21
#

import time
from cmdLineParser import cmdLineParser
from colorizer import colorizer, backColor, textColor, textAttribute    # for text coloration in console mode

from sudoku import sudoku
from ownExceptions import sudokuError

# App. consts
#

CURRENT_VERSION = "0.1.26"

# Command line options
#

CMD_OPTION_CHAR = "-"

CMD_OPTION_SOLVE = "s"
CMD_OPTION_EDIT = "e"
CMD_OPTION_EDIT_AND_SOLVE = "es"
CMD_OPTION_BROWSE = "b"
CMD_OPTION_BROWSE_AND_SOLVE = "bs"

CMD_OPTION_CONSOLE = "c"         # Console mode
CMD_OPTION_DETAILS = "d"         # Show progression details

#
#   Functions
#

# Show usage
#
def _usage(color):
    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.BOLD]))
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_SOLVE + " {srcName} ", formatAttr=[textAttribute.DARK]), ": Find a Sudoku's solution. The file {srcName} the grid to solve")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {sudoName} ", formatAttr=[textAttribute.DARK]), ": Start the edition mode. The file {sudoName} will be created or modified")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT_AND_SOLVE + " {sudoName} ", formatAttr=[textAttribute.DARK]), ": Edit and solve a new grid. the file {sudoName} will be created or modified")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.DARK]), ": Console display mode (if term or nCurses are available)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_BROWSE + " {folder} ", formatAttr=[textAttribute.DARK]), ": Browser the folder {folder}. All contained grids will be displayed")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_BROWSE_AND_SOLVE + " {folder} ", formatAttr=[textAttribute.DARK]), ": Browse the {folder} folder and solve the choosen Sudoku's grid")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " {drawFreq} ",formatAttr=[textAttribute.DARK]),": Draw the grid during resolution process. {drawFreq} is the drawing rate (0 = none, 1 : 100%, 10 = 1/10, 100 = 1/100,  ...")

if __name__ == '__main__':

    color = colorizer(True)

    # Default values for variables
    #
    showUsage = False
    consoleMode = False
    browseFolder = False
    editMode = False
    solveMode = False
    fileName = ""
    folderName = ""
    drawFreq = 0        # don't display progression

    # Parse command line
    #
    parameters = cmdLineParser(CMD_OPTION_CHAR)

    if 0 == parameters.size():
        showUsage = True
    else:
        # Console display mode ?
        consoleMode = not (parameters.findAndRemoveOption(CMD_OPTION_CONSOLE) == parameters.NO_INDEX)

        # Solve mode ?
        index =  parameters.findAndRemoveOption(CMD_OPTION_SOLVE)
        if not parameters.NO_INDEX == index:
            # filename expected
            try :
                rets = parameters.parameterOrValue(index + 1)
                if rets[1] == False : 
                    fileName = rets[0]
                    solveMode = True
            except IndexError:
                # no filename
                showUsage = True
        else:
            # Edition mode ?
            index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT)
            if not parameters.NO_INDEX == index:
                # filename expected
                try :
                    rets = parameters.parameterOrValue(index + 1)
                    if rets[1] == False : 
                        fileName = rets[0]
                        editMode = True
                except IndexError:
                    # no filename ...
                    showUsage = True
            else:
                # Edition & resolution ?
                index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT_AND_SOLVE)
                if not parameters.NO_INDEX == index:
                    # filename expected
                    try :
                        rets = parameters.parameterOrValue(index + 1)
                        if rets[1] == False : 
                            fileName = rets[0]
                            editMode = True
                            solveMode = True
                    except IndexError:
                        # no filename ...
                        showUsage = True
                else:
                    # Parse/browse folder ?
                    index =  parameters.findAndRemoveOption(CMD_OPTION_BROWSE)
                    if not parameters.NO_INDEX == index:
                        # foldername needed
                        try :
                            rets = parameters.parameterOrValue(index + 1)
                            if rets[1] == False : 
                                folderName = rets[0]
                                browseFolder = True
                                editMode = True
                        except IndexError:
                            # no folder given
                            showUsage = True
                    else:
                        # browse and solve ?
                        index =  parameters.findAndRemoveOption(CMD_OPTION_BROWSE_AND_SOLVE)
                        if not parameters.NO_INDEX == index:
                            # foldername needed
                            try :
                                rets = parameters.parameterOrValue(index + 1)
                                if rets[1] == False : 
                                    folderName = rets[0]
                                    browseFolder = True
                                    editMode = True
                                    solveMode = True
                            except IndexError:
                                # no folder given
                                showUsage = True
        
        # display details ?
        index =  parameters.findAndRemoveOption(CMD_OPTION_DETAILS)
        if not parameters.NO_INDEX == index:
            # num value expected
            try :
                rets = parameters.parameterOrValue(index + 1)
                if rets[1] == False : 
                    drawFreq = int(rets[0])
                    drawFreq = drawFreq if drawFreq > 0 else 0
            except IndexError:
                # no value
                showUsage = True

    # There should be no options left
    if parameters.options() > 0 or True == showUsage or (0 == len(fileName) and 0 == len(folderName)):
        _usage(color)
        exit(1)

    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]), "- version", CURRENT_VERSION)

    # my sudoku grid
    solver = None

    # Loading ...
    #
    try:
        solver = sudoku(drawFreq, consoleMode)
        
        if browseFolder:
            if not solver.allowFolderBrowsing():
                raise sudokuError("This display mode is not compatible with folder browsing")
            fileName = solver.browse(folderName)
            if 0 == len(fileName):
                # Cancelled by user
                exit(0)
        else :
            solver.load(fileName, False == editMode)
    except sudokuError as e:
        print(e)
        exit(1)
    except IndexError:
        print("Too many lines in the file")
        exit(1)
    #except:
        #print("Unknown error while loading '" + fileName + "'")
        #exit(1)
        
    # Edition and/or resolution
    #
    try:
        # display starting grid
        solver.showGrid()

        # Edition
        if editMode:
            if False == solver.allowEdition():
                solver.displayText("This display mode is not compatible with grid edition")
                solver.close()
                exit(1)

            # Succefully edited ?
            if False == solver.edit():
                solveMode = False
        
        # Search the solution
        if solveMode:       
            if False == editMode:
                solver.displayText("Press a key to start resolution", False)
                solver.waitForKeyDown()

            solver.displayText("Solving ...", False)
            time.sleep(1)
            attempts, duration = solver.resolve()

            # Display the solution
            solver.showGrid()   

            # A few stats.
            solver.displayText("Resolution duration : " + str(duration) + " second(s)")
            solver.displayText("Attempts : " + str(attempts)) 

            solver.displayText("Press a key to quit", False)
            solver.waitForKeyDown()

        solver.close()

    except sudokuError as e:
        print(e)
    except IndexError:
        print("No soluce found for this grid")
    #except:
    #    print("Unknown error")

# EOF