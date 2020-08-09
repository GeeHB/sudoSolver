# coding=UTF-8
#
#   Fichier     :   sudoku.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets :
#                       - sudoku : "LE" jeu et solver de sudoku
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from element import element, elementStatus
from pointer import pointer

# Affichages
from consoleOutputs import consoleOutputs

class sudoku(object):

    # Données membres
    #
    position_ = None        # Pointeur dans la matrice
    gamePlay_ = []          # Espace de jeu

    # Index des premiers éléments des "petits" carrés (rien ne sert de les calculer !!!)
    squareIndex_ = [0, 3, 6, 27, 30, 33, 54, 57, 60]       

    # Construction
    #
    def __init__(self, fileName = None):
        # Création de la liste vide
        for _ in range(pointer.LINE_COUNT * pointer.ROW_COUNT):
            self.gamePlay_.append(element())

        for i in range(9):
            self.gamePlay_[10*i].setValue(i + 1)

        outputs= consoleOutputs()
        outputs.draw(self.gamePlay_)
        
        if None == fileName :
            # Lecture du fichier source
            self._fromFile(fileName)

    #
    # Méthodes internes
    #

    # Lecture d'un fichier d'archive
    #
    def _fromFile(self, fileName):
        if None == fileName:
            # ???
            return
    
        try:
            file = open(fileName) 
            for line in file: 
                pass
            file.close()
        except FileNotFoundError:
           # Le fichier n'existe pas !
           pass



    # Peut-on mettre cette valeur à la position courante ?
    #

    #   => dans cette ligne ?
    def _checkLine(self, value):
        idFirst = self.position_.line() * pointer.ROW_COUNT 
        for tIndex in range(pointer.ROW_COUNT):
            if self.gamePlay_[tIndex + idFirst].value() == value:
                # La valeur est déja en place
                return False

        # De toute évidence oui
        return True

    #  => dans cette colonne ?
    def _checkRow(self, value):
        idFirst = self.position_.row()

        for tIndex in range(pointer.LINE_COUNT):
            if self.gamePlay_[tIndex * pointer.ROW_COUNT + idFirst].value() == value:
                # La valeur est déja en place
                return False

        # Ok
        return True

    #  => dans ce "petit" carré
    def _checkSquare(self, value):
        tIndex = self.squareIndex_[self.position_.squareID()]      
        for _ in range (3):
            for tRow in range(3):
                if self.gamePlay_[tIndex + tRow].value() == value:
                    # La valeur est déja en place
                    return False
            tIndex+=pointer.ROW_COUNT


        # Pas trouvé
        return True

# Juste pour les tests
#
essai = sudoku()

# EOF