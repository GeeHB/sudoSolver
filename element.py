# coding=UTF-8
#
#   File     :   element.py
#
#   Author      :   JHB
#
#   Description :   Définition de l'objet element : a single sudoku element
#
#   Version     :   0.1.26
#
#   Date        :   2020-09-21
#

#
# elementStatus - Element's status
#
class elementStatus(object):

    EMPTY = 0
    SET = 1
    VALUED = 1
    ORIGINAL = 2        # Can't be changed (except on edition mode)

#
# element - Un élément (ie une case) du Sudoku
#
class element(object):

    # Données membres
    #
    value_ = None                   # Num. value
    status_ = elementStatus.EMPTY   # Current state

    # Construction
    def __init__(self, value = None):
        if not None == value:
            # On construction values are 'original'
            self.value_ = value
            self.status_ = elementStatus.ORIGINAL | elementStatus.SET

    # Gestion de la valeur
    #
    #   Paramètres :
    #           value : valeur numérique de la case (aucune vérification n'est effectuée)
    #           original : la valeur est-elle originale ? Une valeur originale se sera pas modifiée
    #
    def setValue(self, value = None, original = False, editMode = False):
        if False == editMode :
            # La valeur doit-être modifiable
            if not self.status_ and elementStatus.ORIGINAL:
                # Mise à jour de la valeur
                if not value == None:
                    self.value_ = value
                    self.status_ = elementStatus.SET    # J'ai une valeur

                    if True == original:
                        self.status_ |= elementStatus.ORIGINAL

                else:
                    # Effacement de la valeur
                    self.status_ = elementStatus.EMPTY
        else:
            # En mode édition on fait ce que l'on veut ...
            self.value_ = value
            self.status_ = elementStatus.EMPTY if 0 == self.value_ else elementStatus.SET | elementStatus.ORIGINAL

    def value(self):
        return self.value_ if self.status_ & elementStatus.SET else None

    # L'élément est (à nouveau) vide
    # retourne l'ancienne valeur
    def  empty(self):
        self.status_ = elementStatus.EMPTY
        return self.value_

    # Element's status
    #
    def isEmpty(self):
        return self.status_ == elementStatus.EMPTY
    
    def isOriginal(self):
        return ((self.status_ & elementStatus.ORIGINAL) == elementStatus.ORIGINAL)

# EOF