# coding=UTF-8
#
#   Fichier     :   sudoSolver.py
#
#   Auteur      :   JHB
#
#   Description :   Résolution d'une grille de Sudoku
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
CURRENT_VERSION = "0.1.10"

# Options de la ligne de commandes
#

CMD_OPTION_CHAR = "-"            # Une option débute par ce caractère

CMD_OPTION_EDIT = "e"            # Edition d'une (nouvelle) grille
CMD_OPTION_CONSOLE = "c"         # Affichages en mode console (term ou nCurses ni dispo)
CMD_OPTION_DETAILS = "d"         # Niveau de détail (0 = aucun)

#
#   Fonctions
#

# Usage de l'application
#
def _usage(color):
    print(color.colored("\nsudoSolver.py", formatAttr=[textAttribute.GRAS]), "- version", CURRENT_VERSION)
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {destName} ", formatAttr=[textAttribute.FONCE]), ": Lancement en mode édition. Le fichier {destName} est crée ou modifié")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_CONSOLE, formatAttr=[textAttribute.FONCE]), ": Affichage en mode console (term ou nCurses si disponible)")
    print("\t", color.colored(CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " {drawFreq} ",formatAttr=[textAttribute.FONCE]),": Fréqeunce d'affiche des grilles en cours de résolution (0 = aucun, 1 : 100%, 10 = 1/10, 100 = 1/100,  ...")

#
# Point d'entrée de l'application
#

# C'est parti ...
color = colorizer(True)
_usage(color)

try:
    solver = sudoku()
    solver.loadFromFile("/Users/jhenry-barnaudiere/Nextcloud/dev/python/sudoSolver/grid2.txt")
    #solver.loadFromFile("/home/jhb/Nextcloud/dev/python/sudoSolver/grid2.txt")
    
    # Grille d'origine
    solver.showGrid()    
    
    print("Appuyez sur entrée pour lancer la résolution")
    solver.waitKeyDown()

    # C'est parti
    solver.resolve()

    print("Appuyez sur entrée pour terminer")
    solver.waitKeyDown()

except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    # Généré lors du parse du fichier ...
    print("Trop de lignes dans le fichier")
#except:
#    print("Erreur inconnue")

# EOF