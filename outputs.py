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

    # Affichage de toute la matrice
    #  à surcharger
    def draw(self, elements):
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