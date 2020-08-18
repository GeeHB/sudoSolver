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
from ownExceptions import reachedEndOfList

#
# pointer - Pointeur sur une case du Sudoku
#
#   Cet objet effectue les différentes opérations de convertions linéaire <=> matriciel <=> indicaire
#
class pointer(object):

    # Constantes publiques
    #
    INDEX_MIN = 0
    INDEX_MAX = 80

    ROW_COUNT = 9
    LINE_COUNT = 9

    VALUE_MIN = 1
    VALUE_MAX = 9

    # Données membres
    #
    index_      =   INDEX_MIN       # Index de la "case"
    
    row_ = 0                        # Position dans la "matrice"
    line_ = 0
    
    squareID_ = 0                    # Indice du "petit" rectangle

    gameMode_ = False               # En mode "jeu"

    # Construction
    #
    def __init__(self, other = None, index = None, gameMode = True):
        # Copie des paramètres
        #
        if not None == other:
            # Construction par recopie
            self.set(other)
        else:
            self.index_ = 0 if None == index else index
            self.gameMode_ = gameMode 

    # Copie
    #
    def set(self, other):
        self.index_ = other.index_
        self.row_ = other.row_
        self.line_ = other.line_
        self.squareID_ = other.squareID_
        self.gameMode_ = other.gameMode_

    # Accès
    #

    # Index du pointeur
    def index(self):
        return self.index_
    
    # Position
    def row(self):
        return self.row_
    def line(self):
        return self.line_
    def squareID(self):
        return self.squareID_

    #
    # Changement d'index
    #

    # +=
    #
    def __iadd__(self, inc):
        # Incrément
        self.index_ += inc

        # Atteint et dépassé la fin de la liste ?
        if self.index_ > self.INDEX_MAX:
            if True == self.gameMode_ :
                raise reachedEndOfList
            else:
                if self.index_ > (1+self.INDEX_MAX):
                    raise IndexError

        # Calculs ...
        self._whereAmI()
        return self

    # -=
    #
    def __isub__(self, dec):
        # Décrément
        self.index_ -= dec

        # On reste dans la liste
        if self.index_ < self.INDEX_MIN:
            raise IndexError

        # Calculs ...
        self._whereAmI()
        return self

    # Changement de ligne
    #
    def upLine(self):
        self.index_ -= self.ROW_COUNT
        if self.index_ <= self.INDEX_MIN:
            self.index_ = self.row_ + (self.ROW_COUNT - 1) * self.ROW_COUNT
        self._whereAmI()

    def downLine(self):
        self.index_ += self.ROW_COUNT
        if self.index_ >= self.INDEX_MAX:
            self.index_ = self.row_
        self._whereAmI()

    # Changement de coordonnées
    #
    def _whereAmI(self):
        # Mes coordonnées
        self.line_ = math.floor(self.index_ / 9)
        self.row_ = self.index_ - 9 * self.line_

        # Indice du "petit" carré dans lequel je suis me trouve
        self.squareID_ = 3 * math.floor(self.line_ / 3) + math.floor(self.row_ / 3)

# EOF