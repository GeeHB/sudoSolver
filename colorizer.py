# coding=UTF-8
#
#   File     :   colorizer.py
#
#   Author      :   JHB
#
#   Description :   Définition des objets :
#                     - colorizer : Gestion de la colorisation des sorties enmode terminal (et/ou texte)
#                     - textAttribute : Liste des attributs
#                     - textColor : Liste des couleurs de texte
#                     - backColor : Liste des coleurs de fond
#
#   Remarque    :  le module termcolor doit être installé
#
#   Version     :   0.1.25-2
#
#   Date        :   9 mai 2020
#

try :
    # Pour la coloration des sorties terminal
    from termcolor import colored
    packageTermColor = True
except ModuleNotFoundError:
    packageTermColor = False

#
# backColor - Couleurs de fond
#
class backColor:

    GRIS = "on_grey"
    ROUGE = "on_red"
    VERT = "on_green"
    JAUNE = "on_yellow"
    BLEU = "on_blue"
    MAGENTA = "on_magenta"
    CYAN = "on_cyan"
    BLANC = "on_white"

#
# textkColor - Couleurs du texte
#
class textColor:

    GRIS = "grey"
    ROUGE = "red"
    VERT = "green"
    JAUNE = "yellow"
    BLEU = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    BLANC = "white"

#
# colorAttribute - Attributs d'affichage
#
class textAttribute:
    GRAS = "bold"
    FONCE = "dark"
    SOULIGNE = "underline"
    CLIGNTANT = "blink"
    INVERSE = "reverse"
    CACHE = "concealed"

#
#   colorizer  - Colorisation du texte
#
class colorizer:
    # Données membres
    #
    colored_ = False       # Doit-on coloriser ?
    
    # Construction
    def __init__(self, colored = True):
        self.colored_ = colored

        if True == colored and False == packageTermColor:
            self.colored_ = False
            print(self.checkBoxLine(False, "Le package termcolor (python-termcolor) n'est pas installé"))
                        
    # Formatage d'une ligne de texte
    def colored(self, text, txtColor = None, bkColor = None, formatAttr = None):
        # On colorise ou pas ...
        return colored(text, color=txtColor, on_color = bkColor, attrs = formatAttr) if True == self.colored_ else text

    # Début de ligne en mode [OK] / [KO]
    def checkBoxLine(self, checked = True, text = "", color = None):
        box="["
        if True == checked:
            box+=self.colored("OK", textColor.VERT)
        else:
            box+=self.colored("KO", textColor.ROUGE if color == None else color)
        box+="]"
        if len(text) > 0 :
            box+=" "
            box+=text
        return box
# EOF