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
# Constantes internes
#

# Indices des couleurs
COLOUR_EVEN_ID  = 1
COLOUR_ODD_ID   = 2

# "Origine" pour l'affichage de la grille
ORIGIN_X = 5
ORIGIN_Y = 5

#
# cursesOutputs - Affichage de la grille de Sudoku en mode console avec (n)Curses 
#
class cursesOutputs(outputs):

    term_ = None      # Ecran curses

    # Construction
    #
    def __init__(self, showDetails = False):
        # Initialisation de curses
        #
        self.term_ = curses.initscr()
        curses.cbreak()
        self.term_.keypad(True)   # Tous les caractères
        self.term_.nodelay(True)  # Lecture etat clavier non-bloquant
        curses.curs_set(0)        # Pas de curseur

        # des couleurs ?
        if False == curses.has_colors():
            raise sudokuError("Curses doit accepter les couleurs")

        # Initialisation des couleurs
        #
        curses.start_color()

        # "Carrés" pairs
        curses.init_pair(COLOUR_EVEN_ID, curses.COLOR_WHITE, curses.COLOR_BLACK)

        # "Carrés" imparis
        curses.init_pair(COLOUR_ODD_ID, curses.COLOR_BLUE, curses.COLOR_WHITE)

    # Affichage de toute la matrice
    #
    def draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):
                
                # Elément à afficher
                currentElement = elements[position.index()]

                # Attribut et couleur ...
                attr = curses.color_pair(COLOUR_EVEN_ID) if 0 == (position.squareID() % 2) else curses.color_pair(COLOUR_ODD_ID)
                if currentElement.isOriginal():
                    attr |= curses.A_BOLD # Le éléments "originaux" en gras

                # Affichage
                self.term_.addstr(ORIGIN_Y + line, ORIGIN_X + 3 * row, " " + (" " if currentElement.isEmpty() else str(currentElement.value())) +  " ", attr) 
                
                # on avance ...
                position+=1
        
        # Ne pas oublier de mettre à jour l'affichage !
        self.term_.refresh()

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #
    def _update(self, elements, limit):
        # On réaffiche toute la grille ...
        if True == self.drawDetails_:
            self.draw(elements)
    
    # Fin ...
    #
    def close(self):
        # On remet le terminal dans l'état d'origine
        curses.endwin()

 # EOF