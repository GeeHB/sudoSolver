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
#   Version     :   0.1.18
#
#   Date        :   20 aout 2020
#
from outputs import outputs
from element import element, elementStatus
from pointer import pointer

#
# consoleOutputs - Affichages basiques en mode console
#
class consoleOutputs(outputs):
    
    # Affichage de toute la matrice
    #
    def draw(self, elements):
        
        myIndex = 0
        myLine = 0

        print("")

        # Affichage ligne par ligne
        #
        for _ in range(pointer.LINE_COUNT):
            line = ""
            myCol = 0
            for _ in range(pointer.ROW_COUNT):
                currentElement = elements[myIndex]
                line+=" "
                line+= " " if currentElement.isEmpty() else str(currentElement.value())
                line+=" "
                myIndex += 1

                # Changement de carré ?
                myCol += 1
                if 3 == myCol:
                    line += " "
                    myCol = 0
            
            # Fin de ligne
            print(line)
            myLine += 1
            if 3 == myLine:
                # ligne vide entre les "petits" carrés
                myLine = 0
                print("")
 
 # EOF