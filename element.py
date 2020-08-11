# coding=UTF-8
#
#   Fichier     :   element.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet element : une "case" du sudoku
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

#
# elementStatus - Statuts pour un élément
#
class elementStatus(object):

    EMPTY = 0           # La case est vide
    SET = 1
    VALUED = 1
    ORIGINAL = 2        # Valeur qui ne peut être modifiée

#
# element - Un élément (ie une case) du Sudoku
#
class element(object):

    # Données membres
    #
    value_ = None                   # Valeur de la cellule
    status_ = elementStatus.EMPTY   # Par défaut vide

    # Construction
    def __init__(self, value = None):
        if not None == value:
            # C'est une valeur originale
            self.value_ = value
            self.status_ = elementStatus.ORIGINAL | elementStatus.SET

    # Gestion de la valeur
    #
    def setValue(self, value = None):
        # La valeur doit-être modifiable
        if not self.status_ and elementStatus.ORIGINAL:
            # Mise à jour de la valeur
            if not value == None:
                self.value_ = value
                self.status_ = elementStatus.SET    # J'ai une valeur
            else:
                # Effacement de la valeur
                self.status_ = elementStatus.EMPTY

    def value(self):
        return self.value_ if self.status_ & elementStatus.SET else None

    # L'élément est (à nouveau) vide
    # retourne l'ancienne valeur
    def  empty(self):
        self.status_ = elementStatus.EMPTY
        return self.value_

    # Status de l'élément
    #
    def isEmpty(self):
        return self.status_ == elementStatus.EMPTY
    
    def isOriginal(self):
        return self.status_ and elementStatus.ORIGINAL

# EOF