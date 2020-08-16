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

from sudoku import sudoku
from ownExceptions import sudokuError

# Gestion de la grille
#
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