# coding=UTF-8
#
#   Fichier     :   sudoku.py
#
#   Auteur      :   JHB
#
#   Description :   Définition de l'objet :
#                       - sudoku : "LE" jeu et solver de sudoku
#
#   Remarque    :  
#
#   Version     :   0.1.16
#
#   Date        :   19 aout 2020
#

from element import element, elementStatus
from pointer import pointer
from ownExceptions import reachedEndOfList, sudokuError

# Affichage (s) de la grille de Sudoku
from consoleOutputs import consoleOutputs       # Windows et tous les autres OS

#
# Constantes publiques
#

VALUE_SEPARATOR = ","           # Séparateur de valeurs dans les fichiers

#
#   sudoku : Résolution du sudoku
#
#       Les "cases" sont enregistrées dans une liste, ligne après ligne.
#       l'objet "pointer" permet de passer d'une position linéaire au tuple (x, y, "petite" grille") 
#
class sudoku(object):

    # Données membres
    #
    fileName_ = ""          # Nom du fichier courant
    elements_ = []          # Les "cases" de la grille
    outputs_ = None         # Affichage

    # Index des premiers éléments des "petits" carrés (rien ne sert de les calculer !!!)
    squareIndex_ = [0, 3, 6, 27, 30, 33, 54, 57, 60]       

    # Construction
    #
    def __init__(self, detailsRatio = 0, consoleMode = False):

        # Gestion des affichages
        #

        # En mode graphique ?
        if False == consoleMode:
            try:
                from pyOutputs import pyOutputs
                self.outputs_ = pyOutputs()
            except ModuleNotFoundError:
                print("PYGame n'est pas installé. Les affichages seront effectués en mode console")
            except sudokuError as e:
                print(e)

        # ... sinon en mode console
        if None == self.outputs_:
            try:
                from cursesOutputs import cursesOutputs
                self.outputs_ = cursesOutputs()
            except ModuleNotFoundError:
                print("(n)Curses n'est pas installé. Les affichages seront effectués en mode console simple")
            except sudokuError as e:
                print(e)
             
        # Le gestionnaire n'a pu être crée => utilisation de la console
        if None == self.outputs_:
            self.outputs_ = consoleOutputs()

        # Niveau de détail de l'affichage
        self.outputs_.setDetailsRatio(detailsRatio)

        # Création de la liste vide
        for _ in range(pointer.LINE_COUNT * pointer.ROW_COUNT):
            self.elements_.append(element())
        
    # Peut-on éditer une grille ?
    #
    def allowEdition(self):
        return False if None == self.outputs_ else self.outputs_.allowEdition()

    # Attente d'un évènement clavier
    #
    def waitKeyDown(self):
        if not None == self.outputs_:
            self.outputs_.waitForKeyboardInput()

    # Fin des affichages
    #
    def close(self):
        if not None == self.outputs_:
            self.outputs_.close()
    
    # Affichage de la grille
    #
    def showGrid(self):
        self.outputs_.draw(self.elements_)

    # Lecture d'un fichier d'archive
    #
    def load(self, fileName, mustExist):
        if None == fileName or 0 == len(fileName):
            # ???
            raise sudokuError("Pas de nom de fichier")
    
        self.fileName_ = fileName
        
        # On essaye d'ouvir le fichier
        #
        try:
            file = open(fileName)
        except FileNotFoundError:
            # Le fichier n'existe pas !
            if True == mustExist:
                # Il doit être présent => erreur bloquante
                raise sudokuError("Le fichier '" + fileName + "' n'existe pas")
            else:
                # Le fichier n'a pas besoin d'exister
                print("Le fichier '" + fileName + "' n'existe pas")
                return
            
        # Un pointeur !
        pt = pointer(gameMode = False)

        # Parcours des lignes 1 / 1
        for line in file: 

            # Retrait du saut de ligne à la fin
            if line[len(line) - 1] == "\n":
                line = line[:len(line) - 1]

            # Découpage des valeurs
            values = line.split(VALUE_SEPARATOR)

            # Format incorrect pour la ligne
            if not pointer.ROW_COUNT == len(values):
                raise sudokuError("Format invalide pour la ligne n° " + str(pt.line()+1)+ " - " + str(len(values)) + " valeurs")

            # Analyse et ajout des valeurs
            #
            for val in values:
                # Format valide ?
                if val.isnumeric():

                    # Dans [0,9] ?
                    nVal = int(val)
                    if nVal < 0 or nVal > pointer.LINE_COUNT:
                        raise sudokuError("Erreur : la valeur en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ") n'est pas dans le bon intervalle : " + val)

                    # Tentative d'ajout de la valeur "originale"
                    #

                    # La valeur 0 correspond à une case vide
                    if nVal > 0:
                        # Vérification de la ligne
                        if False == self._checkLine(pt, nVal):
                            raise sudokuError("Erreur de ligne : la valeur " + val + " ne peut être mise en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")

                        # Vérification de la colonne
                        if False == self._checkRow(pt, nVal):
                            raise sudokuError("Erreur de colonne : la valeur " + val + " ne peut être mise en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")

                        # Vérification du carré
                        if False == self._checkSquare(pt, nVal):
                            raise sudokuError("Erreur de carré : la valeur " + val + " ne peut être mise en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ")")
                        
                        # Je peux l'ajouter !
                        self.elements_[pt.line() * pointer.ROW_COUNT + pt.row()].setValue(nVal, True)
                else:
                    if (len(val)):
                        raise sudokuError("Erreur : la valeur en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ") n'est pas numérique : " + val)

                # Valeur suivante
                pt += 1

        # Chargement terminé
        file.close()

    # Sauvegarde du fichier
    #
    def save(self):
        
        # Ouverture du fichier
        #
        try:
            file = open(self.fileName_, "w")
            
            # Un pointeur !
            pt = pointer(gameMode = False)
            
            # Parcours de la grille
            for lIndex in range(pointer.LINE_COUNT) :
                line = ""
                for _ in range(pointer.ROW_COUNT):
                    el = self.elements_[pt.index()]
                    line+=str(0 if el.isEmpty() else el.value())
                    line+=VALUE_SEPARATOR

                    # Valeur suivante
                    pt+=1
                
                # Ajout / retrait des séparateurs et sauts de ligne
                line = line[:len(line) - 1]
                if lIndex < (pointer.LINE_COUNT -1):
                    line+="\n"
                
                # Ecriture de la ligne
                file.write(line)
            
            # Terminé
            file.close()
        except:
            raise sudokuError("Erreur lors de l'enregistrement de " + self.fileName_)

    # Edition de la grille
    #
    #   Retourne un boolèen indiquant si la grille a été sauvegardée (ou pas)
    #
    def edit(self):
        # L'édition est impossible
        if None == self.outputs_ or False == self.outputs_.allowEdition():
            return False

        # Edition
        #
        valid = False
        cont = True
        position = pointer(gameMode=False)      # Position actuelle
        prev = None                             # Position précédente (pour l'effacement)
        
        while cont:
            # Effacement de l'ancienne position
            if not None == prev:
                self.outputs_.drawSingleElement(prev.row(), prev.line(), self.elements_[prev.index()].value(), True, self.outputs_.BK_COLOUR, self.outputs_.TXT_COLOUR)
            
            # Affichage de la nouvelle valeur
            self.outputs_.drawSingleElement(position.row(), position.line(), self.elements_[position.index()].value(), True, self.outputs_.SEL_BK_COLOUR, self.outputs_.SEL_TXT_COLOUR)
            self.outputs_.update()
            prev = pointer(position)

            # Analyse du clavier
            #
            key = self.outputs_.waitForKeyboardInput()
            
            # Position du curseur
            #
            if self.outputs_.MOVE_LEFT == key:
                #position -= 1
                position.decRow()
            else:
                if self.outputs_.MOVE_RIGHT == key:
                    #position += 1
                    position.incRow()
                else:
                    if self.outputs_.MOVE_UP == key:
                        position.decLine()
                    else:
                        if self.outputs_.MOVE_DOWN == key:
                            position.incLine()
                        else:
                            # Changement de la valeur de la case
                            #
                            if self.outputs_.VALUE_DEC == key:
                                val = self.elements_[position.index()].value()
                                if None == val : 
                                    val = 0
                                
                                newVal = self._findPreviousValue(position, val)
                                if not newVal == val:
                                    # Mise à jour de la valeur
                                    self.elements_[position.index()].setValue(newVal, True, True)
                                    prev = None
                            else:
                                if self.outputs_.VALUE_INC == key:
                                    val = self.elements_[position.index()].value()
                                    if None == val : 
                                        val = 0
                                    
                                    newVal = self._findNextValue(position, val)
                                    if not newVal == val:
                                        # Mise à jour de la valeur
                                        self.elements_[position.index()].setValue(newVal, True, True)
                                        prev = None
                                else:
                                    # Annulation
                                    if self.outputs_.EDIT_CANCEL == key:
                                        cont = False
                                    else:
                                        # Enregistrement
                                        if self.outputs_.EDIT_QUIT_AND_SAVE == key:
                                            cont = False
                                            valid = True
                                
        # Mise à jour / enregistrement
        if True == valid :
            self.save()
    
    # Résolution de la grille
    #
    def resolve(self):
        try:
            self._resolve()
        except reachedEndOfList:
            # Terminé avec succès
            #self.close()
            return True
        
        # ???
        self.close()
        return False

    #
    # Méthodes internes
    #

    # Méthode interne pour la résolution de la grille de Sudoku
    #
    def _resolve(self):

        candidate = 0
        position = pointer(gameMode = True)             # Un pointeur avec limite
        position = self._findFirstEmptyPos(position)

        # A chaque itération, on considère que la grille est "pleine"
        # jusqu'au pointeur courant - "position"
        # la valeur "candidate" va être tentée à l'emplacement courant du pointeur
        while True :

            candidate +=1

            if candidate > pointer.VALUE_MAX:
                # Aucune valeur n'a été trouvée pour cet emplacement
                # il faut donc reculer jusqu'à la précédente valeur "posée"
                position = self._previousPos(position)

                # Mise à jour de l'affichage
                self.outputs_.updateGrid(self.elements_, position)

                # On repart de la valeur utilisée précédement (que l'on incrémentera au prochain passage)
                candidate = self.elements_[position.index()].empty()
            else :
                # On essaye de positionner la valeur "candidate" à la "position"
                #
                if True == self._checkValue(position, candidate):
                    # La valeur est acceptée (pour l'instant) !!!

                    # Je "pose" la valeur
                    self.elements_[position.index()].setValue(candidate)

                    # Affichage
                    self.outputs_.updateGrid(self.elements_, position)

                    # On avance jusqu'à la position vide suivante
                    position = self._findFirstEmptyPos(position)
                    
                    # On tente toujours avec la plus petite valeur possible
                    candidate = 0 


    # Peut-on mettre cette valeur à la position courante ?
    #
    def _checkValue(self, position, value):
        return self._checkLine(position, value) and self._checkRow(position, value) and self._checkSquare(position, value)

    #   => dans cette ligne ?
    def _checkLine(self, position, value):
        idFirst = position.line() * pointer.ROW_COUNT 
        for tIndex in range(pointer.ROW_COUNT):
            if self.elements_[tIndex + idFirst].value() == value:
                # La valeur est déja en place
                return False

        # De toute évidence oui
        return True

    #  => dans cette colonne ?
    def _checkRow(self, position, value):
        idFirst = position.row()
        for tIndex in range(pointer.LINE_COUNT):
            if self.elements_[tIndex * pointer.ROW_COUNT + idFirst].value() == value:
                # La valeur est déja en place
                return False

        # Ok
        return True

    #  => dans ce "petit" carré
    def _checkSquare(self, position, value):
        tIndex = self.squareIndex_[position.squareID()]      
        for _ in range (3):
            for tRow in range(3):
                if self.elements_[tIndex + tRow].value() == value:
                    # La valeur est déja en place
                    return False
            tIndex+=pointer.ROW_COUNT

        # Valeur non-trouvée => ok
        return True

    # Recherche du premier emplacement vide en avant
    #
    #   Retourne un pointeur sur l'emplacement trouvé
    #   une exeception reachedEndOfList est levée lorsque la fin 
    #   de la liste est atteinte (la grille est donc pleine)
    # 
    def _findFirstEmptyPos(self, start):
        newPos = pointer(start)

        # On avance tant que la case n'est pas vide
        while not self.elements_[newPos.index()].isEmpty():
            newPos += 1
        
        # Terminé
        return newPos

    # Retour à la position précédente (dernière modification) 
    #
    #   Retourne un pointeur sur l'emplacement
    #   une exeception IndexError est levée lorsque
    #   l'on sort de la liste (ie. la grille est surement impossible)
    # 
    def _previousPos(self, current):
        newPos = pointer(current)

        # Je supprime cet élément
        self.elements_[newPos.index()].empty()
        newPos -= 1

        # On recule tant que la case est "originale" (ie. tant qu'elle en peut être modifiée)
        while self.elements_[newPos.index()].isOriginal():
            newPos -= 1
        
        # Terminé
        return newPos

    # Recherche de la première valeur supérieure possible pour la case donnée
    #
    #   Retourne la valeur recherchée ou la valeur initiale (seule valeur possible)
    #
    def _findNextValue(self, position, val):
        nextVal = position.incValue(val)
        while not val == nextVal:
            if self._checkValue(position, nextVal):
                # Trouvée !
                return nextVal
            
            # La prochaine peut-être ?
            nextVal = position.incValue(nextVal)

        
        # Pas d'autre valeur possible
        return nextVal

    # Recherche de la première valeur infèrieure possible pour la case donnée
    #
    #   Retourne la valeur recherchée ou la valeur initiale (seule valeur possible)
    #
    def _findPreviousValue(self, position, val):
        nextVal = position.decValue(val)
        while not val == nextVal:
            if self._checkValue(position, nextVal):
                # Trouvée !
                return nextVal
            
            # La prochaine peut-être ?
            nextVal = position.decValue(nextVal)
               
        # Pas d'autre valeur possible
        return nextVal

# EOF