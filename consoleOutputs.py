# coding=UTF-8
#
#   Fichier     :   consoleOutputs.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet consoleOutputs pour l'affichage en mode console
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from element import element, elementStatus
from pointer import pointer

#
# consoleOutputs - Affichages basiques en mode console
#
class consoleOutputs(object):
    
    # Affichage de toute la matrice
    #
    def draw(self, elements):
        
        myIndex = 0

        # Affichage ligne par ligne
        for _ in range(pointer.LINE_COUNT):
            line = ""
            for _ in range(pointer.ROW_COUNT):
                currentElement = elements[myIndex]
                line+=" "
                line+= " " if currentElement.isEmpty() else str(currentElement.value())
                line+=" "
                myIndex += 1
            
            # Fin de ligne
            print(line)

 # EOF