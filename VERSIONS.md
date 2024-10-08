# *sudoSolver* releases informations

#### Known issues
* No window resizing on Linux
* No multithread on MacOS

#### Dependencies
* Linux - Fedora >= 36
   * termios
   * fcntl
   * termcolor
   * nCcurses
* ChromeOS
   * Linux +
      * tk (sudo apt-get install python3-tk)
* All OS
   * PyGame 2.1.2

#### todo
* Resize "new grid" combo ? https://stackoverflow.com/questions/39915275/change-width-of-dropdown-listbox-of-a-ttk-combobox


#### Version 2.0.1
* july 2024
* Added :
   * Generate new grid (to be solved)
* Corrections :
   * SDL error when closing window

#### Version 1.6.4
* aug. 2023
* Added :
   * systemInfos.py -> sharedTools/systemInfos.py
* Corrections :
   * Keyboard codes for PYGame outputs
   * BUG : Unable to cancel edit mode

#### Version 1.6.3
* 31 july 2023
* Added :
   * getters & setters
   * add systemInfos.py for OS specific informations
   * Keep PYGame window position
      * functionnal on Linux, Windows, ChromeOS (no move but no error !) & MacOS
      * using win32 API for Windows Systems
* Corrections :
   * BUG : Exception raised when tkInter not found (on ChromeOS)
   * BUG : PYGame window created in mode 'pygame.SCALED' on ChromeOS
   * BUG : Unable to close tkWindow on ChromeOS
   * BUG : coredump when browsing a folder in multithreaded mode
   * BUG : Grid Window hang after resolution
   * Output object deleted and created in all cases

#### Version 1.6.2
* 24 jul. 2023
* Added :
   * use argparse for commandline
   * Mouse support for PYGame
   * Enhance keyboard control
      * select direct value (1, ..9)
      * delete a value
   * Exceptions handling (and associated messages)
   * Use "fast" strings : f"{xxx}"
   * Files ordered in browse mode
   * Code factorisation
   * Change progress mode (for GUI)
   * Add icons to GUI (18x18 png files)
   * Error messages sent to stderr
* Bugs correction:
   * clicks outside de grid are ignored
   * singleThreaded and multiThreaded handled by a unique variable
   * GUI : coredumped when passing from singlethreaded to multithreaded mode

#### Version 1.5.9
* 10 nov. 2022
* Added :
   * Print a message when no solution has been found
   * Added : README.md and ./gitHub for captures and logos
   * Added : LICENCE.md
   * Rename files in ./grids (and Added : new ones)
   * Show obvious values
* Bugs correction :
   * Translation errors
   * ModuleNotFoundError exception raised when pyGame is not installed (regression)
   * Multithreaded version not fonctionnal on MacOS (MacOS bugs ???) => force single threaded
   * No stats with nCurses outputs

#### Version 1.5.5
* 18 jul. 2022
* Bugs correction :
   * Segmentation Fault bug correction (due to PYGame)
* (re)added ./sharedTools folder containing cmdLineParser and colorizer classes

#### Version 1.5.3
* 13 jul. 2022
* Bugs corrections :
   * GL is no longer multithreaded !!! (since PyGame 2.xx)
   * Error in mulithreaded mode when closing PyGame (still a seg. error message)
* Added or modifyed :
   * 2 solver modes : threaded (-dd) and non-threaded (-d = default)
   * Added : pygameThreadedOutputs object
      * Dedicated thread to pyGame outputs in multithreaded mode
      * Inherits pygameOutputs & threading.Thread  
      + Based on sync or async "actions" to be performed
   * pygameThreadedOutputs object calls can be monothreaded or multithreaded
   * remove drawingThread.py (now part of pygameThreadedOutputs)

#### Version 1.4.xxx
* 29 jun. 2022
   * use of module sharedTools.common for cmdLineParser and colorizer versions
   * Corrections - bug while parsing command-line - usage display (if no params)

#### Version 1.3.5
* 13 sept. 2021
* Added :
   * element::elementStatus is an enumeration !!! - inherits IntFlag https://docs.python.org/fr/3/library/enum.html ! Very slow => return to simple int (more than 3 times faster !)
   * integrate new interfaces from cmdLineParser.py and colorizer.py

#### Version 1.3.4
* 5 aug. 2021
* Added or modifyed
   * Modifiy outputs.py : now display stats
   * drawing thread is now handled by sudoku object
   * New algo. for obvious values discovering
      * Searches for obvious values for empty places (previous algo.) 
      * Try to set a particular value in another line or row
   * Add tinySquare.py - handles "small" squares
   * Add testing grids 
   * Add "-dd" option for showing progress => display grid (-d)
* Bug fixes and improvments 
   * grid were always saved when edited (even if not modified)
   * Invalid error message when canceling edition (Exception not catched)
   * Escape resolution process on -d(d) mode(s) when "Escape" pressed

#### Version 1.2.4
* 21 jul. 2021
* Minor bug fixes and corrections

#### Version 1.2.2
* 20 jul. 2021
* Added :
   * Mutlithreaded mode
      * a specific thread is dedicated to PYGame's drawings 
      * drawThread.py 
      * -d options (no more freq. ) 
      * PYGame mode : shows obvious values using border colour 
* Fixes and corrections
   * Function protypes corrections
   * "-es {filename}" option checks if {filename} is a real file
   * "-bs {folder}" option checks if {folder} is a real folder
   * fix regression bug for curses and console modes on non-Windows env.

#### Version 1.1.2
* 19 jul. 2021
* Added :
   * Search for obvious values before brute-force searching (-o parameter)
   * options.py : handle parameters and command-line parsing
* Minor bug fixes

#### Version 1.0.0
* 24 dec. 2020
* Release 1
* add sudoku::checkValue for UI purpose - Minor bug fixes

#### Version 0.1.27
* 15 nov. 2020
* Minor bug fixes

#### Version 0.1.26
* 14 nov. 2020
* End of translation in English
* Added :
   * -x option to export solution in a .solution file
* Minor bug fixes :
   * displayed texts
   * regression : console & curses display mode
   * center text of element's value
   * blink text bug (not always visible)
   * purge blinking event when deleting the message

#### Version 0.1.25
* 13 sept. 2020
* Added :
   * Translation in English
   * Add textSurface and blinkingText objects for drawing text on top of sudoku's grid
* Minor bug fixes

#### Version 0.1.24
* 8 sept. 2020
* Start translation of comments an messages
* Added :
   * Display grid's filename - displays on PYGame
   * Added : command line options : + -b (browse and edit in a folder)
   * -bs (browse and solve)
* Minor bug fixes :
   * exit bug on edition mode
   * display bug : selected item redraw on window resize

#### Version 0.1.23
* 2 sept. 2020
* Corrections mineures + regression : 
   * pas d'élément sélectionné par défaut en mode édition
* Ajouts :
   * Fonctionne avec Windows::pygame
   * Optimisations
   * retaille uniquement si la taille est différente

#### Version 0.1.22
* 1er sept. 2020
* Corrections mineures
   * retaille de la police
   * gestion des evt clavier
   * Optimisations
   * affichage du texte
   * "mode" d'affichage
   * Ajout de "l'énumérateur"

#### Version 0.1.20
* 27 aout 2020
* Retaille de la fenêtre (première mouture)
* Corrections mineures

#### Version 0.1.19
* 21 aout 2020
* Tests et non-regression
* Corrections mineures 
   * bug Melk de l'éditeur en (8,8)
* Ajouts
   * Affichages et messages d'erreur
   * Ajout de l'option -es : "Edit and Solve"

#### Version 0.1.18
* 20 aout 2020
* Corrections mineures
   * Bug Melk dans l'éditeur lorsque pos = (0,0)
   * cas des grilles impossibles
* Ajouts
   * Utilisation du module math plus rapide pour les calculs de conversion
   * Ajout des stats (durée et nombre de tentatives)

#### Version 0.1.16
* 19 aout 2020 
* Première version complète - First fonctionnal release

#### Version 0.1.1
* 8 aout 2020 
* Début du projet - Project init.