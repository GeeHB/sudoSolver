# coding=UTF-8
#
#   Fichier     :   pointer.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets :
#                       - pointer : pointeur sur la valeur courante dans le Sudoku
#                       - reachedEndOfList : Exception levée lorsque le pointeur pointe à la fin de la liste
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

import math

# Index min & max
#
INDEX_MIN = 0
INDEX_MAX = 80

# La recherche est terminée (ie, lle pointeur pointe sur la fin de la liste)
class reachedEndOfList(Exception):
    pass

#
# pointer - Pointeur sur une case du Sudoku
#
#   Cet objet effectue les différentes opérations de convertions linéaire <=> matriciel <=> indicaire
#
class pointer:

    # Données membres
    #
    index_      =   INDEX_MIN       # Index de la "case"
    row_ = None                     # Position dans la matrice
    line_ = None
    squareID_ = None                # Indice du "petit" rectangle

    # Construction
    def __init__(self, index = None):
        pass

    # Index du pointeur
    def index(self):
        return self.index_
    
    #
    # Changement d'index
    #

    # Positionnement direct
    def setIndex(self, newIndex):
        if not newIndex == self.index_:
            # Une erreur ?
            if newIndex < INDEX_MIN:
                raise IndexError
            
            # Sorti de la liste ?
            if newIndex > INDEX_MAX:
                raise reachedEndOfList

            self.index_ = newIndex

            # Mes coordonnées
            self.line_ = math.floor(self.index_ / 9)
            self.row_ = self.index_ - 9 * self.line_

            # Indice du carré dans lequel je suis situé
            self.squareID_ = 3 * math.floor(self.line_ / 3) + math.floor(self.row_ / 3)

    # +=
    def __iadd__(self, inc):
        self.setIndex(self.index_ + inc)
    
    # -=
    def __isub__(self, dec):
        self.setIndex(self.index_ + dec)
# EOF