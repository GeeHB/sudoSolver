# coding=UTF-8
#
#   Fichier     :   pyOutputs.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet pyOutputs
#                   Affichages avec la librairie graphique PYGame
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from outputs import outputs

from ownExceptions import reachedEndOfList, sudokuError
from element import element, elementStatus
from pointer import pointer

import pygame

# 
# Constantes internes
#

# Positions et dimensions
#
SQUARE_SIDE         = 80    # Taille d'un "carré"

DELTA_X             = 10    # Décallage horizontal et vertical de la grille
DELTA_Y             = 10

EXT_BORDER_WIDTH    = 3     # Largeur / épaisseur de la bordure extérieure

# Texte
#
FONT_NAME   = 'Helvetica'
FONT_SIZE   = 45

#
# outputs - Affichage de la grille de Sudoku en mode graphique avec PYGame
#
class pyOutputs(outputs):

    # Touches pour les déplacements et les éditions
    #
    MOVE_LEFT           = pygame.K_LEFT
    MOVE_RIGHT          = pygame.K_RIGHT
    MOVE_UP             = pygame.K_UP
    MOVE_DOWN           = pygame.K_DOWN
    
    VALUE_DEC           = pygame.K_w     # Changement de la valeur de la case
    VALUE_INC           = pygame.K_q

    EDIT_CANCEL         = pygame.K_ESCAPE   # Annulation des modifications
    EDIT_QUIT_AND_SAVE  = pygame.K_RETURN   # Fin des modif. et enregistrement
    
    # Données membres
    #
    win_            = None     # "Fenêtre" d'affichage
    
    width_          = 0        # Dimensions de la fenêtre
    height_         = 0
    squareWidth_    = 0        # Dimensions intérieures d'un élément
    textOffset_     = 0

    # Construction
    #
    def __init__(self, showDetails = False):
        # Initialisation de PYGame
        #
    
        # Vérification de PYGame (retourne le tupe (#ok, #errors))
        rets = pygame.init()

        if 0 != rets[1] :
            # Des erreurs !
            raise sudokuError("Erreur - L'initialisation de pygame a retourné " + str(rets[1]) + " erreur(s)")

        # Dimensions
        self.width_ = pointer.ROW_COUNT * SQUARE_SIDE + 2 * DELTA_X
        self.height_ = pointer.LINE_COUNT * SQUARE_SIDE + 2 * DELTA_Y
        self.squareWidth_ = SQUARE_SIDE - 2 * EXT_BORDER_WIDTH
        self.textOffset_ = (SQUARE_SIDE - FONT_SIZE) / 2
        
        # Création de la fenêtre
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)
        pygame.display.set_caption('sudoSolver')

        # On affiche les bordures
        self._drawBorders()

    # Accepte l'édition ?
    #
    def allowEdition(self):
        return True
   
    # En attente de l'appui d'une touche
    #
    def waitForKeyboardInput(self):
        # On attend l'appui sur une touche
        event = pygame.event.wait()
        while not event.type == pygame.KEYDOWN:
            event = pygame.event.wait()
        return event.key

    # Affichage de toute la matrice
    #
    def draw(self, elements):
        position = pointer(gameMode = False)

        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):
                
                # Elément à afficher
                currentElement = elements[position.index()]
                self.drawSingleElement(row, line, currentElement.value(), currentElement.isOriginal(), self.BK_COLOUR, self.TXT_COLOUR)

                # on avance ...
                position+=1

        pygame.display.update()

    # Affichage d'un élément de la matrice
    #
    def drawSingleElement(self, row, line, value, bold, bkColour, txtColour):
        
        x = DELTA_X + row * SQUARE_SIDE + EXT_BORDER_WIDTH
        y = DELTA_Y + line * SQUARE_SIDE + EXT_BORDER_WIDTH
        
        # Le fond
        pygame.draw.rect(self.win_, bkColour, (x, y, self.squareWidth_, self.squareWidth_))

        # La valeur si non nulle
        if not None == value:
            font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
            if bold : font.set_bold(True)
            label = font.render(str(value), 1, txtColour)
            self.win_.blit(label, (x + self.textOffset_, y + self.textOffset_))

    # Mise à jour de l'affichage
    #
    def update(self):
        pygame.display.update()
    
    # Fin des affichages
    #
    def close(self):
        # Fermeture de l'environnement
        pygame.display.quit()

    #
    # Méthodes "privées"
    #

    # Affichage des bordures
    #
    def _drawBorders(self):
        
        # Le fond de la fenêtre
        pygame.draw.rect(self.win_, self.BK_COLOUR, (0, 0, self.width_, self.height_))
        
        # Les "petites" bordures ...
        #
        for line in range(pointer.LINE_COUNT):
            for row in range(pointer.ROW_COUNT):
                x = DELTA_X + row * SQUARE_SIDE
                y = DELTA_Y + line * SQUARE_SIDE
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + SQUARE_SIDE))
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + SQUARE_SIDE), (x + SQUARE_SIDE, y + SQUARE_SIDE))

        # ... puis les bordures extérieures
        #
        lSquare = SQUARE_SIDE * 3
        for line in range(3):
            for row in range(3):
                x = DELTA_X + row * lSquare
                y = DELTA_Y + line * lSquare
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + lSquare), EXT_BORDER_WIDTH)
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + lSquare), (x + lSquare, y + lSquare), EXT_BORDER_WIDTH)
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y + lSquare), (x + lSquare, y), EXT_BORDER_WIDTH)
                pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y), (x, y), EXT_BORDER_WIDTH)

        pygame.display.update()
        
    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #  
    def _update(self, elements, limit):
        # On réaffiche toute la grille ...
        self.draw(elements) 

 # EOF