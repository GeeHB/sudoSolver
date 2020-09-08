# coding=UTF-8
#
#   File     :   outputs.py
#
#   Author      :   JHB
#
#   Description :   Définition de l'objet outputs
#                   Classe abstraite, base tous les affichages
#
#   Version     :   0.1.24
#
#   Date        :   2020-09-08
#

import os
from ownExceptions import sudokuError
from pointer import pointer

#
# outputs - Affichage de la grille de Sudoku 
#
class outputs(object):

    #
    # Constantes publiques
    #

    EVT_KEYDOWN         = None  # By default the event doesn't exist
    EVT_QUIT            = None

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

    #  App colours
    #
    BORDER_COLOUR       = (81, 154, 186)
    BK_COLOUR           = (230, 230, 255)
    BK_COLOUR_FILENAME  = (220, 220, 245)
    TXT_COLOUR          = (64, 64, 64)
    HILITE_COLOUR       = (248, 128, 112)

    SEL_BK_COLOUR       = (50, 50, 255)
    SEL_TXT_COLOUR      = (255, 255, 255)

    # Display modes
    #
    MODE_DEFAULT        = 0 
    MODE_EDIT           = 1
    MODE_BROWSEFOLDER   = 2

    #
    # "private" members
    #

    # Affichage des étape lors de la résolution
    detailsRatio_ = 0          # Taux d'affichage de la progression (0 = aucun)
    detailsCount_ = 0          # Indice d'affichage

    mode_ = MODE_DEFAULT       # Display mode
    gridFileName_ = None

    def setDetailsRatio(self, detailsRatio = 0):
        self.detailsRatio_ = detailsRatio

    # En attente de l'appui d'une touche
    #  à surcharger
    def waitForEvent(self, elements = None, allEvents = False):
        pass

    # Accepte l'édition ?
    def allowEdition(self):
        return not (0 == (self.mode_ & self.MODE_EDIT))

    # Accepte l'analyse des dossier ?
    def allowFolderBrowsing(self):
        return not (0 == (self.mode_ & self.MODE_BROWSEFOLDER))

    # Set/change the current grid's filename
    #   can be overloaded
    def setGridName(self, fileName):
        # the file must exists
        if False == os.path.isfile(fileName):
            raise sudokuError(fileName +  " is not a file")
        self.gridFileName_ = fileName

    # Draw all the grid
    #   can be overloaded
    def draw(self, elements):
       pass

    # Draw asingle element in the grid
    #   can be overloaded
    def drawSingleElement(self, row, line, value, bold, bkColour, txtColour):
        pass

    # Update the display
    #   can be overloaded
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

    # End of the object (no more drawings at all)
    #   can be overloaded
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