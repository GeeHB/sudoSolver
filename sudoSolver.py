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
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from cmdLineParser import cmdLineParser
from colorizer import colorizer, backColor, textColor, textAttribute    # Pour la coloration des sorties terminal

from sudoku import sudoku
from ownExceptions import sudokuError

# Constantes de l'application
#

# Version du programme
CURRENT_VERSION = "0.1.11"

# Options de la ligne de commandes
#

CMD_OPTION_CHAR = "-"            # Une option débute par ce caractère

CMD_OPTION_SRC = "s"             # Résolution de la grille dont le fichier est passé en paramètres
CMD_OPTION_EDIT = "e"            # Edition d'une (nouvelle) grille
CMD_OPTION_CONSOLE = "c"         # Affichages en mode console (term ou nCurses ni dispo)
CMD_OPTION_DETAILS = "d"         # Niveau de détail (0 = aucun)

#
#   Fonctions
#

# Usage de l'application
#
def _usage(color):
    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]))
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_SRC + " {srcName} ", formatAttr=[textAttribute.FONCE]), ": Résolution d'un Sudoku. Le fichier {srcName} contient la grille à résoudre.")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {destName} ", formatAttr=[textAttribute.FONCE]), ": Lancement en mode édition. Le fichier {destName} est crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.FONCE]), ": Affichage en mode console (term ou nCurses si disponible)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " {drawFreq} ",formatAttr=[textAttribute.FONCE]),": Fréqeunce d'affiche des grilles en cours de résolution (0 = aucun, 1 : 100%, 10 = 1/10, 100 = 1/100,  ...")

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
    index =  parameters.findAndRemoveOption(CMD_OPTION_SRC)
    if not parameters.NO_INDEX == index:
        # L'option doit être suivie du nom du fichier
        try :
            rets = parameters.parameterOrValue(index + 1)
            if rets[1] == False : 
                fileName = rets[0]
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

"""
if True == editMode:
    print("Mode édition")
else:
    print("Mode résolution")

print("Fichier :", fileName)
print("Mode console" if True == consoleMode else "Mode graphique")
"""

# C'est parti
#
print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]), "- version", CURRENT_VERSION)

try:
    solver = sudoku(drawFreq, consoleMode)
    solver.loadFromFile(fileName, False == editMode)
    
    if editMode:
        if False == solver.allowEdition():
            print("Ce mode d'affichage ne permet pas l'édition des grilles")
            solver.close()
            exit(1)

        solver.edit()
    else:   
        # Affichage de la grille d'origine
        solver.showGrid()    
        
        print("Appuyez sur entrée pour lancer la résolution")
        solver.waitKeyDown()

        # C'est parti
        solver.resolve()

        print("Appuyez sur entrée pour terminer")
        solver.waitKeyDown()

    # Fermeture des affichage
    solver.close()

except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    # Généré lors du parse du fichier ...
    print("Trop de lignes dans le fichier")
#except:
#    print("Erreur inconnue")

# EOF