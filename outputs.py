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

    # Seulement 1 / GRID_DRAW_FREQ grille sera affichée
    #   permet d'accélerer la résolution
    GRID_DRAW_FREQ_ = 100          

    # Données membres
    #

    # Affichage des étape lors de la résolution
    drawDetails_ = False
    detailsCount_ = 0          # Indice d'affichage

    
    def setDetails(self, drawAll = False):
        self.drawDetails_ = drawAll

    # En attente de l'appui d'une touche
    #  à surcharger
    def waitForKeyboardInput(self):
        pass

    # Affichage de toute la matrice
    #  à surcharger
    def draw(self, elements):
       pass

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #
    def update(self, elements, limit):
        # Mise à jour ?
        self.detailsCount_ += 1
        if 0 == (self.detailsCount_ % self.GRID_DRAW_FREQ_):
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