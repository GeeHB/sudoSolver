# coding=UTF-8
#
#   File        :   options.py
#
#   Author      :   JHB
#
#   Description :   Handle command-line
#
#   Version     :   1.2.3
#
#   Date        :   2021-07-20
#

from cmdLineParser import cmdLineParser
from colorizer import colorizer, textAttribute

CURRENT_VERSION = "1.2.3"

# Command line options
#

CMD_OPTION_CHAR = "-"           # Parameters starts with ...

CMD_OPTION_SOLVE = "s"
CMD_OPTION_EDIT = "e"
CMD_OPTION_EDIT_AND_SOLVE = "es"
CMD_OPTION_BROWSE = "b"
CMD_OPTION_BROWSE_AND_SOLVE = "bs"
CMD_OPTION_SEARCH_OBVIOUS = "o"

CMD_OPTION_SAVE_SOLUCE      = "x"

CMD_OPTION_CONSOLE = "c"         # Console mode
CMD_OPTION_DETAILS = "d"         # Show progression details

#
#   options object : command-line parsing and parameters management
#
class options(object):

    # Construction
    #
    def __init__(self):

        # Default values
        self.color_ = colorizer(True)
        self.showUsage_ = False
        self.consoleMode_ = False
        self.browseFolder_ = False
        self.editMode_ = False
        self.solveMode_ = False
        self.fileName_ = ""
        self.folderName_ = ""
        self.drawProgress_ = False        # don't display progression
        self.exportSoluce_ = False
        self.obviousValues = False

    # Browse the command line
    #   returns True when ok
    def parse(self):

        showUsage = False
        parameters = cmdLineParser(CMD_OPTION_CHAR)
        if 0 == parameters.size():
            showUsage = True
        else:
            # Console display mode ?
            self.consoleMode_ = not (parameters.findAndRemoveOption(CMD_OPTION_CONSOLE) == parameters.NO_INDEX)

            # Export the solution ?
            self.exportSoluce_ = not (parameters.findAndRemoveOption(CMD_OPTION_SAVE_SOLUCE) == parameters.NO_INDEX)

            # Search obvious values ?
            self.obviousValues_ = not (parameters.findAndRemoveOption(CMD_OPTION_SEARCH_OBVIOUS) == parameters.NO_INDEX)

            # Solve mode ?
            index =  parameters.findAndRemoveOption(CMD_OPTION_SOLVE)
            if not parameters.NO_INDEX == index:
                # File name expected
                try :
                    rets = parameters.parameterOrValue(index + 1)
                    if rets[1] == False : 
                        self.fileName_ = rets[0]
                        self.solveMode_ = True
                except IndexError:
                    # no filename
                    showUsage = True
            else:
                # Edition mode ?
                index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT)
                if not parameters.NO_INDEX == index:
                    # File name expected
                    try :
                        rets = parameters.parameterOrValue(index + 1)
                        if rets[1] == False : 
                            self.fileName_ = rets[0]
                            self.editMode_ = True
                    except IndexError:
                        # no filename ...
                        showUsage = True
                else:
                    # Edition & resolution ?
                    index =  parameters.findAndRemoveOption(CMD_OPTION_EDIT_AND_SOLVE)
                    if not parameters.NO_INDEX == index:
                        # File name expected
                        try :
                            rets = parameters.parameterOrValue(index + 1)
                            if rets[1] == False : 
                                self.fileName_ = rets[0]
                                self.editMode_ = True
                                self.solveMode_ = True
                        except IndexError:
                            # no filename ...
                            showUsage = True
                    else:
                        # Parse/browse folder ?
                        index =  parameters.findAndRemoveOption(CMD_OPTION_BROWSE)
                        if not parameters.NO_INDEX == index:
                            # foldername needed
                            try :
                                rets = parameters.parameterOrValue(index + 1)
                                if rets[1] == False : 
                                    self.folderName_ = rets[0]
                                    self.browseFolder_ = True
                                    self.editMode_ = True
                            except IndexError:
                                # no folder given
                                showUsage = True
                        else:
                            # browse and solve ?
                            index =  parameters.findAndRemoveOption(CMD_OPTION_BROWSE_AND_SOLVE)
                            if not parameters.NO_INDEX == index:
                                # foldername needed
                                try :
                                    rets = parameters.parameterOrValue(index + 1)
                                    if rets[1] == False : 
                                        self.folderName_ = rets[0]
                                        self.browseFolder_ = True
                                        self.editMode_ = True
                                        self.solveMode_ = True
                                except IndexError:
                                    # no folder given
                                    showUsage = True
            
            # display progression ?
            self.drawProgress_ = not (parameters.findAndRemoveOption(CMD_OPTION_DETAILS) == parameters.NO_INDEX)

        # Export solution => solverMode activated
        if self.exportSoluce_ and not self.solveMode_:
            showUsage = True

        # There should be no options left
        if True == showUsage or parameters.options() > 0 or (0 == len(self.fileName_) and 0 == len(self.folderName_)):
            self.usage()
            return False
        
        # Done
        return True

    # Show usage
    #
    def usage(self):
        if None == self.color_:
            # ???
            return

        print(self.color_.colored("\nsudoSolver.py", formatAttr=[textAttribute.BOLD]), "- release", CURRENT_VERSION, "\n")
        print("\t", self.color_.colored("  " + CMD_OPTION_CHAR + CMD_OPTION_BROWSE + " {srcFolder} ", formatAttr=[textAttribute.DARK]), ": Browse {srcFolder} and display contained grids")
        print("\t", self.color_.colored("  " + CMD_OPTION_CHAR + CMD_OPTION_SOLVE + " {srcName} ", formatAttr=[textAttribute.DARK]), ": Find a solution for the grid saved in {srcName}")
        print("\t", self.color_.colored("  " + CMD_OPTION_CHAR + CMD_OPTION_EDIT + " {srcName} ", formatAttr=[textAttribute.DARK]), ": Edit or create the file {srcName}")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_BROWSE_AND_SOLVE + " {srcFolder} ]", formatAttr=[textAttribute.DARK]), ": Browse {srcFolder} and solve the choosen grid")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_CONSOLE + " ]", formatAttr=[textAttribute.DARK]), ": Console display mode (if term or nCurses are available)")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_DETAILS + " ]",formatAttr=[textAttribute.DARK]),": Draw the grid during resolution process")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_EDIT_AND_SOLVE + " {srcName} ]", formatAttr=[textAttribute.DARK]), ": Edit and solve the sudoku in {srcName}")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SEARCH_OBVIOUS + " ]", formatAttr=[textAttribute.DARK]),": Search for obvious vals before \"brute-force\" soluce searching")
        print("\t", self.color_.colored("[ " + CMD_OPTION_CHAR + CMD_OPTION_SAVE_SOLUCE + " ]", formatAttr=[textAttribute.DARK]),": Save the solution of the grid in a file - {srcName}.soluce")

# EOF