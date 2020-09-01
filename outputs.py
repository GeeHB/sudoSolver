# coding=UTF-8
#
#   Fichier     :   outputs.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet outputs
#                   Classe abstraite, base tous les affichages
#
#   Version     :   0.1.21
#
#   Date        :   28 aout 2020
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
    MOVE_LEFT           = "s"     # Déplacement dans la grille
    MOVE_RIGHT          = "f"
    MOVE_UP             = "e"
    MOVE_DOWN           = "x"
    
    VALUE_DEC           = "+"     # Changement de la valeur de la case
    VALUE_INC           = "-"

    EDIT_CANCEL         = "q"    # Annulation des modifications
    EDIT_QUIT_AND_SAVE  = "w"    # Fin des modif. et enregistrement

    #  Quelques couleurs
    #
    BORDER_COLOUR   = (81, 154, 186)
    BK_COLOUR       = (230, 230, 255)
    TXT_COLOUR      = (64, 64, 64)
    RED_COLOUR      = (248, 128, 112)

    SEL_BK_COLOUR   = (50, 50, 255)
    SEL_TXT_COLOUR  = (255, 255, 255)

    # Modes d'affichages
    #
    MODE_DEFAULT        = 0     # Rien de particulier
    MODE_EDIT           = 1     # Edition possible
    MODE_BROWSEFOLDER   = 2     # Parcours des dossiers

    # Données membres
    #

    # Affichage des étape lors de la résolution
    detailsRatio_ = 0          # Taux d'affichage de la progression (0 = aucun)
    detailsCount_ = 0          # Indice d'affichage

    mode_ = MODE_DEFAULT       # Mode d'affichage

    
    def setDetailsRatio(self, detailsRatio = 0):
        self.detailsRatio_ = detailsRatio

    # En attente de l'appui d'une touche
    #  à surcharger
    def waitForEvent(self, elements = None):
        pass

    # Accepte l'édition ?
    # à surcharger
    def allowEdition(self):
        return not (0 == (self.mode_ & self.MODE_EDIT))

    # Accepte l'analyse des dossier ?


    # Affichage de toute la matrice
    #  à surcharger
    def draw(self, elements):
       pass

    # Affichage d'un élément de la matrice
    # à surcharger
    def drawSingleElement(self, row, line, value, bold, bkColour, txtColour):
        pass

    # Mise à jour de l'affichage
    # à surcharger
    def update(self):
        pass

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #
    def updateGrid(self, elements, limit):
        
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