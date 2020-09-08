# coding=UTF-8
#
#   File     :   pyOutputs.py
#
#   Author      :   JHB
#
#   Description :   Définition de l'objet pyOutputs
#                   Affichages avec la librairie graphique PYGame
#
#   Version     :   0.1.24
#
#   Date        :   2020-09-08
#

from outputs import outputs

from ownExceptions import reachedEndOfList, sudokuError
from element import element, elementStatus
from pointer import pointer

import pygame
import math

# 
# Constantes internes
#

# Positions et dimensions
#
SQUARE_SIDE         = 60    # Taille initiale d'un "carré"

SQUARE_MIN          = 10   # Taille min

DELTA_X             = 10    # Décallage horizontal et vertical intial de la grille
DELTA_Y             = 10

EXT_BORDER_WIDTH    = 3     # Largeur / épaisseur de la bordure extérieure

# Texte
#
APP_FONT_NAME           = 'Herculanum,Papyrus,Helvetica'
APP_FONT_VAL_SIZE       = 35    # Taille par défaut en pixels

FILE_FONT_NAME          = 'Helvetica,Arial'
FILE_FONT_SIZE          = 25
FILE_FONT_POS_X         = 35
FILE_FONT_POS_Y         = 5

ERASE_NAME_AFTER        = 2000  # in ms

#
# outputs - Affichage de la grille de Sudoku en mode graphique avec PYGame
#
class pyOutputs(outputs):

    EVT_KEYDOWN         = pygame.KEYDOWN
    EVT_QUIT            = pygame.QUIT
    
    # Surcharge des touches pour les déplacements et les éditions
    #
    MOVE_LEFT           = pygame.K_LEFT
    MOVE_RIGHT          = pygame.K_RIGHT
    MOVE_UP             = pygame.K_UP
    MOVE_DOWN           = pygame.K_DOWN
    
    VALUE_DEC           = pygame.K_e        # Changement de la valeur de la case
    VALUE_INC           = pygame.K_r

    EDIT_CANCEL         = pygame.K_ESCAPE   # Annulation des modifications
    EDIT_QUIT_AND_SAVE  = pygame.K_RETURN   # Fin des modif. et enregistrement
    
    # Données membres
    #
    win_            = None     # My window
    
    width_          = 0        # Window's dimensions
    height_         = 0
    
    
    intSquareWidth_ = 0        # internal dims of an element
    extSquareWidth_ = 0        # ext. dims 
    
    deltaW_         = 0        # Offsets
    deltaH_         = 0
    
    textOffset_     = 0        # Font handling
    fontSize_       = 0
    font_           = None

    nameSurface_    = None     # Display gridname
    namePos_        = (0,0)
    nameEvent_      = None
    
    # Construction
    #
    def __init__(self, showDetails = False):
        # Initialisation de PYGame
        #
    
        self.mode_ = self.MODE_EDIT + self.MODE_BROWSEFOLDER

        # Vérification de PYGame (retourne le tupe (#ok, #errors))
        rets = pygame.init()

        if 0 != rets[1] :
            # Des erreurs !
            raise sudokuError("Erreur - L'initialisation de pygame a retourné " + str(rets[1]) + " erreur(s)")

        # Dimensions
        self.width_ = pointer.ROW_COUNT * SQUARE_SIDE + 2 * DELTA_X
        self.height_ = pointer.LINE_COUNT * SQUARE_SIDE + 2 * DELTA_Y
        self.extSquareWidth_ = SQUARE_SIDE
        self.intSquareWidth_ = SQUARE_SIDE - 2 * EXT_BORDER_WIDTH
        self.deltaW_ = DELTA_X
        self.deltaH_ = DELTA_Y
        
        # La police et les infos. d'affichage
        self.fontSize_ = APP_FONT_VAL_SIZE
        self.textOffset_ = (SQUARE_SIDE - APP_FONT_VAL_SIZE) / 2
                
        # window creation
        self._setWindowSize()
        pygame.display.set_caption('sudoSolver')

        self._drawBackground()

        # my own event
        self.nameEvent_ = pygame.USEREVENT + 1
   
    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents):
        # On attend l'appui sur une touche ou la retaille de la fenêtre
        finished = False
        while not finished:
            event = pygame.event.wait()
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN :
                finished = True
            elif event.type == pygame.VIDEORESIZE:
                # Update members
                self._onResizeWindow(event.w, event.h)
                
                # Resize the surface
                self._setWindowSize()

                # Draw bkgrnd & lines ...
                self._drawBackground()

                # ... and the grid's content
                if not None == elements:
                    self.draw(elements)
                
                # returns all events ?
                if True == allEvents:
                    finished = True
            elif event.type == self.nameEvent_:
                # erase the name
                if self.nameSurface_:                    
                    del self.nameSurface_
                    self.nameSurface_ = None
                    
                    self._drawBackground()
                    self.draw(elements)
                    self.update()

                pygame.time.set_timer(self.nameEvent_, 0)
                if True == allEvents:
                    finished = True

        return event

    # Set/change the current grid's filename
    #   overloaded
    def setGridName(self, fileName):
        super().setGridName(fileName)

        font = pygame.font.SysFont(FILE_FONT_NAME, FILE_FONT_SIZE)
        self.nameSurface_ = font.render(fileName, 1, self.TXT_COLOUR, outputs.BK_COLOUR_FILENAME)
        
        # Position
        self.namePos_ = (FILE_FONT_POS_X, FILE_FONT_POS_Y)
        
        # erase this name after a while ...
        pygame.time.set_timer(self.nameEvent_, ERASE_NAME_AFTER)

    
    # Draw all the content of the current grid
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

        self.update()

    # Affichage d'un élément de la matrice
    #
    def drawSingleElement(self, row, line, value, highLighted, bkColour, txtColour):
        
        # too small to be drawn ?
        if 0 == self.extSquareWidth_ :
            return
        
        # top-left corner position
        x = self.deltaW_ + row * self.extSquareWidth_ + EXT_BORDER_WIDTH
        y = self.deltaH_ + line * self.extSquareWidth_ + EXT_BORDER_WIDTH
        
        # Erase background
        pygame.draw.rect(self.win_, bkColour, (x, y, self.intSquareWidth_, self.intSquareWidth_))

        # The value (if valid)
        if not None == value:
            if highLighted : 
                #font.set_bold(True)
                txtColour = self.HILITE_COLOUR
            
            label = self.font_.render(str(value), 1, txtColour)
            self.win_.blit(label, (x + self.textOffset_, y + self.textOffset_))

    # Mise à jour de l'affichage
    #
    def update(self):
        # Display filename ?
        if self.nameSurface_:
            # draw the name
            self.win_.blit(self.nameSurface_, self.namePos_)
        pygame.display.update()
    
    # Fin des affichages
    #
    def close(self):
        # close the display
        pygame.display.quit()

    #
    # Méthodes "privées"
    #

    # Gestion de la retaille de la fenêtre
    #
    def _onResizeWindow(self, newWidth, newHeight):

        # Mise à jour des variables d'affichage
        #

        self.width_ = newWidth
        self.height_ = newHeight

        # Taille d'une case
        squareW = math.floor((newWidth - 2 * DELTA_X) / pointer.ROW_COUNT)
        squareH = math.floor((newHeight - 2 * DELTA_Y) / pointer.LINE_COUNT)

        if squareW < SQUARE_MIN or squareH < SQUARE_MIN :
            self.extSquareWidth_ = SQUARE_MIN
        
        # On se base sur le plus petit des 2
        if squareW < squareH :
            self.extSquareWidth_ = squareW
        else:
            self.extSquareWidth_ = squareH

        self.intSquareWidth_ = self.extSquareWidth_ - 2 * EXT_BORDER_WIDTH
        
        # Position de la première case
        self.deltaW_ = math.floor((newWidth - pointer.ROW_COUNT * self.extSquareWidth_) / 2)
        self.deltaH_ = math.floor((newHeight - pointer.LINE_COUNT * self.extSquareWidth_) / 2)

        # Taille de la police
        self.fontSize_ = int(APP_FONT_VAL_SIZE * self.intSquareWidth_ / SQUARE_SIDE)
        self.textOffset_ = (self.extSquareWidth_ - self.fontSize_) / 2 

    # Affichage du fond et des bordures
    #
    def _drawBackground(self):
        
        # Le fond de la fenêtre
        self.win_.fill(self.BK_COLOUR)

        if not 0 == self.extSquareWidth_ : 
            
            # Les "petites" bordures ...
            #
            for line in range(pointer.LINE_COUNT):
                for row in range(pointer.ROW_COUNT):
                    x = self.deltaW_ + row * self.extSquareWidth_
                    y = self.deltaH_ + line * self.extSquareWidth_
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + self.extSquareWidth_))
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + self.extSquareWidth_), (x + self.extSquareWidth_, y + self.extSquareWidth_))

            # ... puis les bordures extérieures
            #
            lSquare = self.extSquareWidth_ * 3
            for line in range(3):
                for row in range(3):
                    x = self.deltaW_ + row * lSquare
                    y = self.deltaH_ + line * lSquare
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y), (x, y + lSquare), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x, y + lSquare), (x + lSquare, y + lSquare), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y + lSquare), (x + lSquare, y), EXT_BORDER_WIDTH)
                    pygame.draw.line(self.win_, self.BORDER_COLOUR, (x + lSquare, y), (x, y), EXT_BORDER_WIDTH)

        self.update()

    # Retaille de la fenêtre et de la surface associée
    #
    def _setWindowSize(self):
        # Suppression des anciens objet
        #
       
        # Police
        if not None == self.font_:
            del self.font_
        self.font_ = pygame.font.SysFont(APP_FONT_NAME, self.fontSize_)

        # Nouvelles dimensions pour la fenêtre et la "surface"
        self.win_ = pygame.display.set_mode((self.width_, self.height_), pygame.RESIZABLE)

        
    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    #  
    def _update(self, elements, limit):
        # On réaffiche toute la grille ...
        self.draw(elements) 

 # EOF