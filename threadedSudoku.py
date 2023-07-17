# coding=UTF-8
#
#   File        :   threadedSudoku.py
#
#   Author      :   GeeHB
#
#   Description :   sudoku object executed by its own thread 
#

from sudoku import sudoku
import ownThread

from options import FILE_EXPORT_EXTENSION, FILE_EXPORT_EXTENSION, options as opts

from element import element, elementStatus
from pointer import pointer, LINE_COUNT, ROW_COUNT, VALUE_MIN, VALUE_MAX, INDEX_MIN, INDEX_MAX

from ownExceptions import reachedEndOfList, sudokuError

#
#   sudoku : Edition and/or resolution of a single sudoku grid
#
class threadedSudoku(sudoku, ownThread.Thread):
    # Construction
    #
    def __init__(self, consoleMode = False, progressMode = opts.PROGRESS_NONE):
        super().__init__(consoleMode, progressMode, False)

        # Start the current thread
        super().initiate()

    # Destruction
    #
    def __del__(self):
        self._addAction(id=ownThread.ACTION_END_THREAD, wait=True)
   
    #
    # Methods overloaded from sudoku object
    #

    # Display the grid and its content
    #
    def displayGrid(self):
        action = ownThread.threadAction(ownThread.ACTION_DRAW_GRID)
        action.params_ = ()
        self._addAction(action)

    # Display a grid stored on a file
    #
    #   return True if grid has been successfully loaded
    #
    def gridFromFile(self, fileName, nameOnGrid = True):
        action = ownThread.threadAction(ownThread.ACTION_GRID_FROM_FILE)
        action.params_ = (fileName, nameOnGrid)
        self._addAction(action)

    # Where all the stuff is done
    #
    def run(self):

        # Try to init PYGame
        self._createPYGameOutputs()
        
        # Action list is free
        self.accessList_.set()

        # Ready to start !
        self.ready_ = True
        over = False
        
        # Actions !!!
        #
        while not over:
            if True == self.newAction_.wait():
                # Do all the "actions"
                over = self._handleActions()

    #
    # "Internal" methods
    #   

    # "Do" / perform the actions in the internal list
    #
    #   returns thread should be ended ?
    #
    def _handleActions(self):

        # Access to the list
        if False == self.accessList_.wait(ownThread.MAX_THREAD_LIST_WAIT):
            # Impossible to access the list
            return (False, None)

        # Block list access
        self.accessList_.clear()

        # Transfer content to a working list
        workingList = []
        for action in self.actions_:
            workingList.append(action)

        # The list is free (and empty)
        self.actions_.clear()

        # Allow other thread to add new actions
        self.newAction_.clear()
        self.accessList_.set()

        endThread = False

        for action in workingList:
            # Handle action
            if ownThread.ACTION_END_THREAD == action.actionId_:
                endThread = True
            elif ownThread.ACTION_DRAW_GRID == action.actionId_:
                self._int_displayGrid()
            elif ownThread.ACTION_GRID_FROM_FILE == action.actionId_:
                self._int_gridFromFile(action.params_[0], action.params_[1])

        return endThread

# EOF