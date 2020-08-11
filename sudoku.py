# coding=UTF-8
#
#   Fichier     :   sudoku.py
#
#   Auteur      :   JHB
#
#   Description :   Définition des objets :
#                       - sudoku : "LE" jeu et solver de sudoku
#                       - sudokuError : Exception
#
#   Remarque    :  
#
#   Version     :   x.x.x
#
#   Date        :   8 aout 2020
#

from element import element, elementStatus
from pointer import pointer, reachedEndOfList

# Affichages
from outputs import outputs
from consoleOutputs import consoleOutputs

#
# Constantes publiques
#

VALUE_SEPARATOR = ","           # Séparateur de valeurs dans les fichiers

#
# sudokuError : Une erreur ...
#
class sudokuError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

#
#   sudoku : Résolution du sudoku
#
class sudoku(object):

    # Données membres
    #
    elements_ = []          # Espace de jeu

    # Index des premiers éléments des "petits" carrés (rien ne sert de les calculer !!!)
    squareIndex_ = [0, 3, 6, 27, 30, 33, 54, 57, 60]       

    # Construction
    #
    def __init__(self, fileName = None):
        # Création de la liste vide
        for _ in range(pointer.LINE_COUNT * pointer.ROW_COUNT):
            self.elements_.append(element())
        
        if not None == fileName :
            # Lecture du fichier source
            self._fromFile(fileName)
        else:
            for i in range(9):
                self.elements_[10*i].setValue(i + 1)

        # Test
        outputs= consoleOutputs()
        outputs.draw(self.elements_)

    # Résolution de la grille de Sudoku
    #
    def resolve(self):

        candidate = 0
        position = pointer(gameMode = True)             # Un pointeur avec limite
        position = self._findFirstEmptyPos(position)

        # A chaque itération, on considère ques la grille est "pleine"
        # jusqu'au pointeur courant
        # la valeur "candidate" va être tentée à l'emplacement courant du pointeur
        while True :

            candidate +=1

            if candidate > pointer.VALUE_MAX:
                # Aucune valeur n'a été trouvée pour cet emplacement
                # il faut donc reculer jusqu'à la précédente valeur "posée"
                position = self._previousPos(position)

                # On repart de la valeur (que l'on incrémentera au prochain passage)
                candidate = self.elements_[position.index()].empty()
            else :
                if True == self._checkValue(position, candidate):
                    # La valeur est bonne !!!
                    self.elements_[position.index()].setValue(candidate)   # Je pose la valeur
                    
                    # On avance jusqu'à la position vide suivante
                    position = self._findFirstEmptyPos(position)
                    
                    # On tente toujours avec la plus petite valeur possible
                    candidate = 0 

    #
    # Méthodes internes
    #

    # Lecture d'un fichier d'archive
    #
    def _fromFile(self, fileName):
        if None == fileName:
            # ???
            return sudokuError("Pas de om de fichier")
    
        try:
            file = open(fileName)
        except FileNotFoundError:
           # Le fichier n'existe pas !
           raise sudokuError("Le fichier '" + fileName + "' n'existe pas")
            
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
                raise sudokuError("Format invalide pour la ligne n° " + str(pt.line()+1))

            # Analyse et ajout des valeurs
            #
            for val in values:
                # Format valide ?
                if val.isnumeric():

                    # Dans [1,9] ?
                    nVal = int(val)
                    if nVal <= 0 or nVal >= pointer.LINE_COUNT:
                        raise sudokuError("Erreur : la valeur en (" + str(pt.line() + 1) + "," + str(pt.row()+1) + ") n'est pas dans le bon intervalle : " + val)

                    # Tentative d'ajout de la valeur "originale"
                    #

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

        file.close()
        
        # Chargement terminé
        return True

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

        # valeur non-trouvée => ok
        return True

    # Recherche du premier emplacement vide en avant
    #
    #   Retourne un pointeur sur l'emplacement
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

    # Retour au précédent emplacement
    #
    #   Retourne un pointeur sur l'emplacement
    #   une exeception IndexError est levée lorsque
    #   l'on sort de la liste
    # 
    def _previousPos(self, current):
        newPos = pointer(current)

        # Je supprime cet élément
        #self.elements_[newPos.index()].empty()
        newPos -= 1

        # On recule tant que la case est "originale"
        while self.elements_[newPos.index()].isOriginal():
            newPos -= 1
        
        # Terminé
        return newPos

# Juste pour les tests
#
try:
    essai = sudoku("d:\\nextcloud\\dev\\python\\sudosolver\\grid1.txt")
except sudokuError as e:
    # Une erreur "Sudoku" => affichage du message
    print(e)
except IndexError:
    print("Trop de lignes dans le fichier")
#except:
#    print("Erreur inconnue")

# EOF