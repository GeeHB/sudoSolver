# coding=UTF-8
#
#   Fichier     :   ownExceptions.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des exceptions utilisées dans le projet :
#                       - sudoku : La solution a été trouvée
#                       - sudokuError : Exception avec message d'erreur
#
#   Remarque    :  
#
#   Version     :   0.1.16
#
#   Date        :   19 aout 2020
#

#
# reachedEndOfList : La recherche est terminée (ie, lle pointeur pointe sur la fin de la liste)
#
class reachedEndOfList(Exception):
    pass

#
# sudokuError : Une erreur ...
#
class sudokuError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message