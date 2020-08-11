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

    # Données membres
    currentPointer_ = None          # Pointeur sur la position courante dans la matrice
    
    # Affichage de toute la matrice
    def draw(self, elements):
       pass

    # Mise à jour de l'affichage (affichage jusqu'au pointeur 'limit')
    def update(self, elements, limit):
        # Par défaut pas de mise à jour ...
        pass

 # EOF