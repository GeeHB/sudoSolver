# coding=UTF-8
#
#   Fichier     :   outputs.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet outputs
#                   Classe abstraite, base tous les affichages
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from pointer import pointer

#
# outputs - Affichage de la grille de Sudoku 
#
class outputs(object):

    #
    # Constantes publiques
    #

    # Touches pour les déplacements et les éditions
    #
    MOVE_LEFT           = 1     # Déplacement dans la grille
    MOVE_RIGHT          = 2
    
    VALUE_DEC           = 3     # Changement de la valeur de la case
    VALUE_INC           = 4

    EDIT_CANCEL         = 5     # Annulation des modifications
    EDIT_QUIT_AND_SAVE  = 6     # Fin des modif. et enregistrement

    # Données membres
    #

    # Affichage des étape lors de la résolution
    detailsRatio_ = 0          # Taux d'affichage de la progression (0 = aucun)
    detailsCount_ = 0          # Indice d'affichage

    
    def setDetailsRatio(self, detailsRatio = 0):
        self.detailsRatio_ = detailsRatio

    # En attente de l'appui d'une touche
    #  à surcharger
    def waitForKeyboardInput(self):
        pass

    # Accepte l'édition ?
    # à surcharger
    def allowEdition(self):
        # Par défaut pas d'édition
        return False

    # Edition de la grille
    # à surcharger
    def edit(self, elements):
        return False        # Rien n'a été modifié

    # Affichage de toute la matrice
    #  à surcharger
    def draw(self, elements):
       pass

    # Affichage d'un élément de la matrice
    # à surcharger
    def drawSingleElement(self, row, line, value, bold, bkColour, txtColour):
        pass

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #
    def update(self, elements, limit):
        
        if self.detailsRatio_ > 0 :
            # Mise à jour de l'affichage ?
            #
            self.detailsCount_ += 1
            if 0 == (self.detailsCount_ % self.detailsRatio_):
                self._update(elements, limit)
                self.detailsCount_ = 0

    # Fin des affichages
    #  à surcharger
    def close(self):
        pass

    #
    # Méthodes "privées"
    #

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #  à surcharger
    def _update(self, elements, limit):
      # Par défaut on ne fait rien
      pass  

 # EOF