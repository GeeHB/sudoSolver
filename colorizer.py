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
#                     - backColor : Liste des couleurs de fond
#
#   Remarque    :  le module termcolor doit être installé
#
#   Version     :   0.1.26
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

    GREY = GRIS = "on_grey"
    RED = ROUGE = "on_red"
    GREEN = VERT = "on_green"
    YELLOW = JAUNE = "on_yellow"
    BLUE = BLEU = "on_blue"
    MAGENTA = "on_magenta"
    CYAN = "on_cyan"
    WHITE = BLANC = "on_white"

#
# textkColor - Couleurs du texte
#
class textColor:

    GREY = GRIS = "grey"
    RED = ROUGE = "red"
    GREEN = VERT = "green"
    YELLOW = JAUNE = "yellow"
    BLUE = BLEU = "blue"
    MAGENTA = "magenta"
    CYAN = "cyan"
    WHITE = BLANC = "white"

#
# colorAttribute - Attributs d'affichage
#
class textAttribute:
    BOLD = GRAS = "bold"
    DARK = FONCE = "dark"
    UNDERLINE = SOULIGNE = "underline"
    BLINK = CLIGNOTANT = "blink"
    REVERSE = INVERSE = "reverse"
    CONCELED = CACHE = "concealed"

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
            print(self.checkBoxLine(False, "termcolor package (python-termcolor) is not installed"))
                        
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