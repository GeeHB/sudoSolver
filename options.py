# coding=UTF-8
#
#   File        :   options.py
#
#   Author      :   GeeHB
#
#   Description :   Handle command-line & shared consts.
#

import sysconfig
from sharedTools import cmdLineParser as parser
from sharedTools import colorizer as color

CURRENT_VERSION = "1.6.1"

# Command line options
#

CMD_OPTION_CHAR = "-"                   # Parameters start with ...

CMD_OPTION_BROWSE = "b"                 # Browse a folder
CMD_OPTION_EDIT = "e"                   # Edit (and modify or create) a grid
CMD_OPTION_SOLVE = "s"                  # Search for a solution for the grid

CMD_OPTION_BROWSE_AND_SOLVE = "bs"
CMD_OPTION_EDIT_AND_SOLVE = "es"

CMD_OPTION_SEARCH_OBVIOUS = "o"         # Search for obvious values

CMD_OPTION_SAVE_SOLUTION = "x"          # Export the solution

CMD_OPTION_CONSOLE = "c"                # Console mode

# Show grid during the search process
CMD_OPTION_SHOW_DETAILS = "d"           # Singlethreaded - all grids are displayed => very slow
CMD_OPTION_SHOW_DETAILS_MT = "dd"       # Multithreaded - not all grids are displayed

#
#   options object : command-line parsing and parameters management
#
class options(object):

    # Construction
    #
    def __init__(self):

        # Default values
        self.color_ = color.colorizer(True, False)
        self.consoleMode_ = False
        self.browseFolder_ = False
        self.editMode_ = False
        self.solveMode_ = False
        self.fileName_ = ""
        self.folderName_ = ""
        self.exportSolution_ = False
        self.obviousValues = False              # don't search "obvious" values before trying to solve
        self.multiThreadedProgress_ = False     # Draw the grid during the search process
        self.singleThreadedProgress_ = False    # Draw "slowly" the grid during search process

    # Browse the command line
    #   returns True when ok
    def parse(self):
        if False == self._parse():
            self.usage()
            return False
        return True

    def _parse(self):

        parameters = parser.cmdLineParser(CMD_OPTION_CHAR)
        
        # Parameters needed
        if 0 == parameters.size():
            return False
        
        # Console display mode ?
        self.consoleMode_ = not (parameters.findAndRemoveOption(CMD_OPTION_CONSOLE) == parameters.NO_INDEX)

        # Export the solution ?
        self.exportSolution_ = not (parameters.findAndRemoveOption(CMD_OPTION_SAVE_SOLUTION) == parameters.NO_INDEX)

        # Search obvious values ?
        self.obviousValues_ = not (parameters.findAndRemoveOption(CMD_OPTION_SEARCH_OBVIOUS) == parameters.NO_INDEX)

        # Solve mode ?
        rets = parameters.getOptionValue(CMD_OPTION_SOLVE)
        if False == rets[1] and rets[0] != None:
            # File name expected
            self.fileName_ = rets[0]
            self.solveMode_ = True
        else:
            # Edition mode ?
            rets = parameters.getOptionValue(CMD_OPTION_EDIT)
            if False == rets[1] and rets[0] != None:
                self.fileName_ = rets[0]
                self.editMode_ = True                
            else:
                # Edition & resolution ?
                rets = parameters.getOptionValue(CMD_OPTION_EDIT_AND_SOLVE)
                if False == rets[1] and rets[0] != None:
                    self.fileName_ = rets[0]
                    self.editMode_ = True
                    self.solveMode_ = True                    
                else:
                    # Parse/browse folder ?
                    rets = parameters.getOptionValue(CMD_OPTION_BROWSE)
                    if False == rets[1] and rets[0] != None:
                        self.folderName_ = rets[0]
                        self.browseFolder_ = True
                        self.editMode_ = True                        
                    else:
                        # browse and solve ?
                        rets = parameters.getOptionValue(CMD_OPTION_BROWSE_AND_SOLVE)
                        if not rets is None and False == rets[1] and rets[0] != None:
                            self.folderName_ = rets[0]
                            self.browseFolder_ = True
                            self.editMode_ = True
                            self.solveMode_ = True
                        else:
                            showUsage = True
        
        # display progression?
        self.singleThreadedProgress_ = not (parameters.NO_INDEX == parameters.findAndRemoveOption(CMD_OPTION_SHOW_DETAILS))
        
        # display grid in multithreaded mode ?
        self.multiThreadedProgress_ = not (parameters.NO_INDEX == parameters.findAndRemoveOption(CMD_OPTION_SHOW_DETAILS_MT))
        if True == self.multiThreadedProgress_:
            # Check if macOS
            if -1 != sysconfig.get_platform().find("macos"):
                print("No multi-threading on macos")
                self.multiThreadedProgress_ = False
                self.singleThreadedProgress_ = True
            else:
                self.singleThreadedProgress_ = False

        # Export solution => solverMode should be activated
        if self.exportSolution_ and not self.solveMode_:
            return False

        # There should be no options left and no errors ...
        if parameters.options() > 0 or (0 == len(self.fileName_) and 0 == len(self.folderName_)):
            return False
        
        # Done
        return True

    # Show usage
    #
    def usage(self, fullUsage = True):
        if None == self.color_:
            # ???
            return

        print(self.color_.colored("\nsudoSolver.py", formatAttr=[color.textAttribute.BOLD]), "by GeeHB - release", CURRENT_VERSION, "\n")
            
        # Show all commands ?
        if True == fullUsage:
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_BROWSE + " {srcFolder} ]", formatAttr=[color.textAttribute.DARK]), ": Browse {srcFolder} and display contained grids")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SOLVE + " {srcName} ]", formatAttr=[color.textAttribute.DARK]), ": Find a solution for the grid saved in {srcName}")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {srcName} ]", formatAttr=[color.textAttribute.DARK]), ": Edit or create the file {srcName}")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_BROWSE_AND_SOLVE + " {srcFolder} ]", formatAttr=[color.textAttribute.DARK]), ": Browse {srcFolder} and solve the choosen grid")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_EDIT_AND_SOLVE + " {srcName} ]", formatAttr=[color.textAttribute.DARK]), ": Edit and solve the sudoku stored in {srcName}")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_CONSOLE + " ]", formatAttr=[color.textAttribute.DARK]), ": Console display mode (if term or nCurses are available)")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SHOW_DETAILS_MT + " ]",formatAttr=[color.textAttribute.DARK]),": Draw the grid during resolution process - multithreaded mode")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SHOW_DETAILS + " ]",formatAttr=[color.textAttribute.DARK]),": Show each tested grid - single threaded mode")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SEARCH_OBVIOUS + " ]", formatAttr=[color.textAttribute.DARK]),": Search for obvious vals before brute-force solution searching")
            print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SAVE_SOLUTION + " ]", formatAttr=[color.textAttribute.DARK]),": Save the solution of the grid in a file - {srcName}.solution")

# EOF