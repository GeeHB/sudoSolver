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

from sudoku import sudoku,sudokuError

# Juste pour les tests
#
try:
    essai = sudoku()
    #essai.loadFromFile("/Users/jhenry-barnaudiere/Nextcloud/dev/python/sudoSolver/grid2.txt")
    essai.loadFromFile("/home/jhb/Nextcloud/dev/python/sudoSolver/grid2.txt")
    essai.resolve()
    
    essai.showGrid()
except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    # Généré lors du parse du fichier ...
    print("Trop de lignes dans le fichier")
except:
    print("Erreur inconnue")

# EOF