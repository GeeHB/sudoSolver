# coding=UTF-8
#
#   Fichier     :   cursesOutputs.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet cursesOutputs pour l'affiche avec la librairie Curses (Unix / LINUX et MAcOS)
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from outputs import outputs

from ownExceptions import reachedEndOfList, sudokuError
from element import element, elementStatus
from pointer import pointer


import curses

#
# cursesOutputs - Affichage de la grille de Sudoku avec Curses 
#
class cursesOutputs(outputs):

    term_ = None      # Ecran curses

    # Construction
    #
    def __init__(self, showDetails = False):
        # Initialisation de curses
        self.term_ = curses.initscr()
        curses.cbreak()
        self.term_.keypad(True)   # Tous les caractères
        self.term_.nodelay(True)  # Lecture etat clavier non-bloquant
        curses.curs_set(0)        # Pas de curseur

    # Affichage de toute la matrice
    def draw(self, elements):
       pass

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    def update(self, elements, limit):
        # On réaffiche toute la grille ...
        if True == self.drawDetails_:
            self.draw(elements)
    
    # Fin ...
    def close(self):
        # On remet le terminal dans l'état d'origine
        curses.endwin()

 # EOF