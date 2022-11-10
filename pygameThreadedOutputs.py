# coding=UTF-8
#
#   File        :   pygameThreadedOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of pygameThreadedOutputs and pygameActions objecte
#                   for threaded version of pygameOutputs class
#                   
#                   pygameThreadedOutputs inherits pygameOutputs class
#

import threading
from pygameOutputs import pygameOutputs

#
# Internal constants
#

# Wait for list availability
MAX_LIST_WAIT = 5  # in sec.

# Actions
#
ACTION_NONE = 0  # Nothing to do

ACTION_DRAW_BKGRND = 1
ACTION_DRAW_GRID = 2
ACTION_DRAW_ELEMENT = 3
ACTION_DRAW_TEXT = 4
ACTION_GRID_NAME = 5

ACTION_UPDATE = 10
ACTION_REFRESH = 11

ACTION_SOLVING_STARTED = 20
ACTION_SOLVING_ENDED = 21

ACTION_CHECK_KEYPRESSED = 30  # Sync event
ACTION_WAIT_EVENT = 31

ACTION_END_THREAD = 999


#
# pygameAction : Single drawing action
#
class pygameAction(object):
    # Members
    #
    actionId_ = ACTION_NONE  # What to do ...
    uid_ = 0  # Unique id
    sync_ = False  # Synchronized with the calling thread ?
    params_ = ()  # Optionnal parameters (depends on action)

    # Construction
    def __init__(self, id=ACTION_NONE):
        self.uid_ = 0
        self.actionId_ = id


#
# pygameThreadedOutputs - Display sudoku's grid using PYGame library
#
class pygameThreadedOutputs(pygameOutputs, threading.Thread):
    # Members
    #
    ready_ = False  # Am I ready ?
    actions_ = []  # Actions (to perform)

    syncRet_ = {}  # Returns from a sync-action
    lastId_ = 0

    newAction_ = threading.Event()  # Notifies the thread a new action is to be performed
    accessList_ = threading.Event()  # Is action-list free ?
    syncThreads_ = threading.Event()  # Event for threads synchronisation

    # Construction
    #
    def __init__(self):

        threading.Thread.__init__(self)  # Create the new thread
        self.start()  # start the thread (ie. call run() method )

    #
    # Methods overloaded from outputs
    #

    # Ready to go ?
    def isReady(self):
        return self.ready_

    # Display text
    #
    def displayText(self, text, information, elements):
        if information:
            super().displayText(text, True, elements)
        else:
            action = pygameAction(ACTION_DRAW_TEXT)
            action.params_ = (text, elements)

            self._addAction(action)

    # Set/change the current grid's filename
    #   overloaded
    def setGridName(self, fileName):
        action = pygameAction(ACTION_GRID_NAME)
        action.params_ = (fileName, "")

        self._addAction(action)

    # Draw the whole grid
    #
    def draw(self, elements):
        action = pygameAction(ACTION_DRAW_GRID)
        action.params_ = (elements, "")
        self._addAction(action)

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row, line, value, bkColour, txtColour):

        # too small to be drawn ?
        if 0 == self.extSquareWidth_:
            return

        # Create the action
        action = pygameAction(ACTION_DRAW_ELEMENT)
        action.params_ = (row, line, value, bkColour, txtColour)

        # Add it to the async. todo list
        self._addAction(action)

    # Update the window
    #
    def update(self):
        self._addAction(id=ACTION_UPDATE)

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements):
        # Create the action
        action = pygameAction(ACTION_SOLVING_STARTED)
        action.params_ = (elements, "")

        # Add it to the async. todo list
        self._addAction(action)

    # Solving process ended
    #   can be overloaded
    def endedSolving(self):
        self._addAction(id=ACTION_SOLVING_ENDED)

    # Tell the thread to close
    def close(self):
        self._addAction(id=ACTION_END_THREAD, wait=True)
        # print("no more thread")

    # Is a key pressed ?
    #
    #   returns the tuple (pressed?, key or None if not pressed)
    #
    def keyPressed(self, elements=None, allEvents=False):
        # Create the action
        action = pygameAction(ACTION_CHECK_KEYPRESSED)
        action.params_ = (elements, allEvents)

        # Add it as a sync action
        return self._addAction(action, wait=True)

    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents):
        # Create the action
        action = pygameAction(ACTION_WAIT_EVENT)
        action.params_ = (elements, allEvents)

        # Add it as a sync action
        return self._addAction(action, wait=True)

    #
    # Methods overloaded from pygameOutputs
    #

    # Draw window's background and grid's borders
    #
    def _drawBackground(self):
        self._addAction(id=ACTION_DRAW_BKGRND)

    # Refresh the whole window
    #
    def _refresh(self, elements):
        action = pygameAction(ACTION_REFRESH)
        action.params_ = (elements, "")
        self._addAction(action)

    #
    # Method overloaded from threading.Thread
    #   

    # Where all the stuff is done
    #
    def run(self):
        # At this point the thread is running ...
        #  

        # Try to init PYGame
        self._start()
        self._int_drawBackground()  # Show an empty grid

        # Action list is free
        self.accessList_.set()

        # Ready to start !
        self.ready_ = True
        over = False
        elements = None

        # Actions !!!
        #
        while not over:
            if True == self.newAction_.wait():
                # Do all the "actions"
                over, elements = self._handleActions(elements)

                # Wait for end of solving process ?
                while elements is not None:
                    self._int_draw(elements)
                    if True == self.newAction_.wait(0.1):
                        # Do all the "actions"
                        over, elements = self._handleActions(elements)

        # Finished !!!
        # super().close()

    #
    # "Internal" methods
    #   

    # Add an action to the internal list
    # 
    def _addAction(self, action=None, id=None, wait=False):

        # Action or id must be present
        if action == None and id == None:
            return False

        # Valid action id ?
        if (action != None and action.actionId_ == ACTION_NONE) or (
                action == None and id == ACTION_NONE) or False == self.accessList_.wait(MAX_LIST_WAIT):
            return False

        # Take list ownership
        self.accessList_.clear()

        # Add new action to the list
        if None == action:
            action = pygameAction(id)

        # Should I think both threads ?
        action.sync_ = wait

        # Wait for action completion ?
        if True == wait:
            self.syncThreads_.clear()  # Should be useless !

        # Add to list (with uid)
        self.lastId_ = self.lastId_ + 1
        action.uid_ = self.lastId_
        self.actions_.append(action)

        # List is now free
        self.accessList_.set()

        # There's a new action to perform
        self.newAction_.set()

        # Wait for completion ...
        if True == wait:
            if action.actionId_ != ACTION_END_THREAD:

                self.syncThreads_.wait()

                # done ...
                self.syncThreads_.clear()

                # handle return
                try:
                    return self.syncRet_[action.uid_]
                except:
                    return False

        # Done
        return True

    # "Do" / perform the actions in the internal list
    #
    #   returns the tuple (thread should be ended ?, Grid if solving or None)
    #
    def _handleActions(self, elements):

        # Access to the list
        if False == self.accessList_.wait(MAX_LIST_WAIT):
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

            # Any drawings to do ?
            if elements is not None:
                self._int_draw(elements)

            # Handle action
            if ACTION_END_THREAD == action.actionId_:
                # super().close()
                endThread = True
            elif ACTION_GRID_NAME == action.actionId_:
                self._int_setGridName(action.params_[0])
            elif ACTION_DRAW_TEXT == action.actionId_:
                self._int_displayText(action.params_[0], action.params_[1])
            elif ACTION_DRAW_BKGRND == action.actionId_:
                self._int_drawBackground()
            elif ACTION_DRAW_GRID == action.actionId_:
                self._int_draw(action.params_[0])
            elif ACTION_DRAW_ELEMENT == action.actionId_:
                self._int_drawSingleElement(action.params_[0], action.params_[1], action.params_[2], action.params_[3],
                                            action.params_[4])
            elif ACTION_UPDATE == action.actionId_:
                self._int_update()
            elif ACTION_REFRESH == action.actionId_:
                self._int_refresh(action.params_[0])
            elif ACTION_SOLVING_STARTED == action.actionId_:
                elements = action.params_[0]
            elif ACTION_SOLVING_ENDED == action.actionId_:
                # No more drawings
                elements = None
            elif ACTION_CHECK_KEYPRESSED == action.actionId_:
                self.syncRet_[action.uid_] = self._int_keyPressed(action.params_[0], action.params_[1])
            elif ACTION_WAIT_EVENT == action.actionId_:
                self.syncRet_[action.uid_] = self._int_waitForEvent(action.params_[0], action.params_[1])

            # Should I sync. ? (ie. should I notify the calling thread ?)
            if True == action.sync_:
                self.syncThreads_.set()

        return (endThread, elements)

# EOF
