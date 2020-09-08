#!/usr/bin/env python3

# coding=UTF-8
#
#   File        :   sudoSolver.py
#
#   Author      :   JHB
#
#   Description :   Display and solve a sudoku grid
#
#   Version     :   0.1.24
#
#   Date        :   2020-09-08
#

from cmdLineParser import cmdLineParser
from colorizer import colorizer, backColor, textColor, textAttribute    # Pour la coloration des sorties terminal

from sudoku import sudoku
from ownExceptions import sudokuError

# App. consts
#

CURRENT_VERSION = "0.1.24"

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
    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]))
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_SOLVE + " {srcName} ", formatAttr=[textAttribute.FONCE]), ": Résolution d'un Sudoku. Le fichier {srcName} contient la grille à résoudre")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {sudoName} ", formatAttr=[textAttribute.FONCE]), ": Lancement en mode édition. Le fichier {sudoName} sera crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT_AND_SOLVE + " {sudoName} ", formatAttr=[textAttribute.FONCE]), ": Edition et résolution d'une nouvelle grille. Le fichier {sudoName} sera crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.FONCE]), ": Affichage en mode console (term ou nCurses si disponible)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_BROWSE + " {folder} ", formatAttr=[textAttribute.FONCE]), ": Affichage et édition des grilles de sudokus contenus dans le dossier {folder}")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_BROWSE_AND_SOLVE + " {folder} ", formatAttr=[textAttribute.FONCE]), ": Affichage du contenu de {folder} puis résolution du sudoku sélectionné")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.FONCE]), ": Affichage en mode console (term ou nCurses si disponible)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " {drawFreq} ",formatAttr=[textAttribute.FONCE]),": Fréquence d'affichage des grilles lors de la résolution (0 = aucun, 1 : 100%, 10 = 1/10, 100 = 1/100,  ...")

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
                # Mode édition & résolution ?
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
        
        # display details
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
                print("This display mode is not compatible with grid edition")
                solver.close()
                exit(1)

            # Succefully edited ?
            if False == solver.edit():
                solveMode = False
        
        # Search the solution
        if solveMode:       
            if False == editMode:
                print("Press a key to start resolution")
                solver.waitForKeyDown()

            print("Let's go ...")
            attempts, duration = solver.resolve()

            # Display the solution
            solver.showGrid()   

            # A few stats.
            print("Resoltion duration : ", duration, " second(s)")
            print("Attempts : ", attempts) 

            print("Press a key to quit")
            solver.waitForKeyDown()

        solver.close()

    except sudokuError as e:
        print(e)
    except IndexError:
        print("No solution found for this grid")
    #except:
    #    print("Unknown error")

# EOF