# coding=UTF-8
#
#   Fichier     :   sudoSolver.py
#
#   Auteur      :   JHB
#
#   Description :   Affichage & résolution d'une grille de Sudoku
#
#   Remarque    :  
#
#   Version     :   0.1.20
#
#   Date        :   27 aout 2020
#

from cmdLineParser import cmdLineParser
from colorizer import colorizer, backColor, textColor, textAttribute    # Pour la coloration des sorties terminal

from sudoku import sudoku
from ownExceptions import sudokuError

# Constantes de l'application
#

# Version du programme
CURRENT_VERSION = "0.1.20"

# Options de la ligne de commandes
#

CMD_OPTION_CHAR = "-"            # Une option débute par ce caractère

CMD_OPTION_SOLVE = "s"           # Résolution de la grille dont le fichier est passé en paramètres
CMD_OPTION_EDIT = "e"            # Edition d'une (nouvelle) grille
CMD_OPTION_EDIT_AND_SOLVE = "es"

CMD_OPTION_CONSOLE = "c"         # Affichages en mode console (term ou nCurses ni dispo)
CMD_OPTION_DETAILS = "d"         # Niveau de détail (0 = aucun)

#
#   Fonctions
#

# Usage de l'application
#
def _usage(color):
    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]))
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_SOLVE + " {srcName} ", formatAttr=[textAttribute.FONCE]), ": Résolution d'un Sudoku. Le fichier {srcName} contient la grille à résoudre")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {sudoName} ", formatAttr=[textAttribute.FONCE]), ": Lancement en mode édition. Le fichier {sudoName} sera crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT_AND_SOLVE + " {sudoName} ", formatAttr=[textAttribute.FONCE]), ": Edition et résolution d'une nouvelle grille. Le fichier {sudoName} sera crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.FONCE]), ": Affichage en mode console (term ou nCurses si disponible)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " {drawFreq} ",formatAttr=[textAttribute.FONCE]),": Fréquence d'affichage des grilles lors de la résolution (0 = aucun, 1 : 100%, 10 = 1/10, 100 = 1/100,  ...")

#
# Point d'entrée de l'application
#

# C'est parti ...
color = colorizer(True)

# Valeurs par défaut des paramètres de l'application
#
showUsage = False
consoleMode = False
editMode = False
solveMode = False
fileName = ""
drawFreq = 0        # Pas d'affichage de la progression

# Analyse de la ligne de commandes
#
parameters = cmdLineParser(CMD_OPTION_CHAR)

if 0 == parameters.size():
    showUsage = True
else:
    # Mode console ?
    consoleMode = not (parameters.findAndRemoveOption(CMD_OPTION_CONSOLE) == parameters.NO_INDEX)

    # Résolution ?
    index =  parameters.findAndRemoveOption(CMD_OPTION_SOLVE)
    if not parameters.NO_INDEX == index:
        # L'option doit être suivie du nom du fichier
        try :
            rets = parameters.parameterOrValue(index + 1)
            if rets[1] == False : 
                fileName = rets[0]
                solveMode = True
        except IndexError:
            # Pas de nom de fichier
            showUsage = True
    else:
        # Mode édition ?
        index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT)
        if not parameters.NO_INDEX == index:
            # L'option doit être suivie du nom du fichier
            try :
                rets = parameters.parameterOrValue(index + 1)
                if rets[1] == False : 
                    fileName = rets[0]
                    editMode = True
            except IndexError:
                # Pas de nom de fichier
                showUsage = True
        else:
            # Mode édition & résolution ?
            index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT_AND_SOLVE)
            if not parameters.NO_INDEX == index:
                # L'option doit être suivie du nom du fichier
                try :
                    rets = parameters.parameterOrValue(index + 1)
                    if rets[1] == False : 
                        fileName = rets[0]
                        editMode = True
                        solveMode = True
                except IndexError:
                    # Pas de nom de fichier
                    showUsage = True
    
    # Niveau de détails
    index =  parameters.findAndRemoveOption(CMD_OPTION_DETAILS)
    if not parameters.NO_INDEX == index:
        # L'option doit être suivie d'une valeur numérique
        try :
            rets = parameters.parameterOrValue(index + 1)
            if rets[1] == False : 
                drawFreq = int(rets[0])
                drawFreq = drawFreq if drawFreq > 0 else 0  # Dans un intervalle gérable
        except IndexError:
            # Pas de valeur
            showUsage = True

# Il ne devrait plus y avoir d'options
if parameters.options() > 0 or True == showUsage or 0 == len(fileName):
    _usage(color)
    exit(1)

# C'est parti
#
print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]), "- version", CURRENT_VERSION)

# Ma grille de Sudoku
solver = None

# Chargement
#
try:
    solver = sudoku(drawFreq, consoleMode)
    solver.load(fileName, False == editMode)
except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    # Généré lors du parse du fichier ...
    print("Trop de lignes dans le fichier")
    exit(1)
#except:
 #   print("Erreur inconnue lors de la lecture de '" + fileName + "'")
 #   exit(1)
    
# Edition et/ou résolution
#
try:
    # Affichage de la grille d'origine
    solver.showGrid()

    # Edition
    if editMode:
        if False == solver.allowEdition():
            print("Ce mode d'affichage ne permet pas l'édition des grilles")
            solver.close()
            exit(1)

        solver.edit()
    
    # Résolution
    if solveMode:       
        if False == editMode:
            print("Appuyez sur une touche pour lancer la résolution")
            solver.waitForKeyDown()

        print("C'est parti ...")
        attempts, duration = solver.resolve()

        # Affichage de la grille terminée
        solver.showGrid()   

        # Quelques stats.
        print("Durée de résolution : ", duration, " seconde(s)")
        print("Tentatives : ", attempts) 

        print("Appuyez sur une touche pour terminer")
        solver.waitForKeyDown()

    # Fermeture des affichage
    solver.close()

except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    print("La grille n'a pas de solution")
#except:
#    print("Erreur inconnue")

# EOF