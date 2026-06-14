# coding=UTF-8
#
#   File        :   pygameThreadedOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of pygameThreadedOutputs and threadActions objecte
#                   for threaded version of pygameOutputs class
#
#                   pygameThreadedOutputs inherits pygameOutputs class
#

import pygame.event
from pygameOutputs import pygameOutputs
from ownThread import threadAction, Thread, MAX_THREAD_LIST_WAIT

#
# pygameThreadedOutputs - Display sudoku's grid using PYGame library
#
class pygameThreadedOutputs(pygameOutputs, Thread):

    # Construction
    #
    def __init__(self, position = None):

        self.position_ = position

        # Start the current thread
        super().initiate()

    #
    # Methods overloaded from outputs
    #

    # Ready to go ?
    def isReady(self) -> bool:
        return self.ready_

    # Display text
    #
    def displayText(self, text, information, elements):
        if information:
            super().displayText(text, True, elements)
        else:
            action = threadAction(threadAction.ACTION_DRAW_TEXT)
            if action is not None:
                action.params_ = [text, elements]
                self._addAction(action)

    # Set/change the current grid's filename
    #   overloaded
    def setGridName(self, fileName, create = False):
        action = threadAction(threadAction.ACTION_GRID_NAME)
        action.params_ = [fileName, ""]

        self._addAction(action)

    # Draw the whole grid
    #
    def draw(self, elements):
        action = threadAction(threadAction.ACTION_DRAW_GRID)
        action.params_ = [elements, ""]
        self._addAction(action)

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row, line, value, bkColour, txtColour):

        # too small to be drawn ?
        if 0 == self.extSquareWidth_:
            return

        # Create the action
        action = threadAction(threadAction.ACTION_DRAW_ELEMENT)
        action.params_ = [row, line, value, bkColour, txtColour]

        # Add it to the async. todo list
        self._addAction(action)

    # Update the window
    #
    def update(self):
        self._addAction(id=threadAction.ACTION_UPDATE)

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements):
        # Create the action
        action = threadAction(threadAction.ACTION_SOLVING_STARTED)
        action.params_ = [elements, ""]

        # Add it to the async. todo list
        self._addAction(action)

    # Solving process ended
    #   can be overloaded
    def endedSolving(self):
        self._addAction(id=threadAction.ACTION_SOLVING_ENDED)

    # Tell the thread to close
    def close(self):
        self._addAction(id=threadAction.ACTION_END_THREAD, wait=True)
        # print("no more thread")

    # Check current/last event
    #
    def pollEvent(self, elements=None, allEvents=False)  -> pygame.event.Event:
        # Create the action
        action = threadAction(threadAction.ACTION_POLL_EVENT)
        action.params_ = [elements, allEvents]

        # Add it as a sync action
        self._addAction(action, wait=True)
        return pygame.event.Event(0)

    # Is a key pressed ?
    #
    #   returns the list (pressed?, key or None if not pressed)
    #
    def keyPressed(self, elements=None, allEvents=False):
        # Create the action
        action = threadAction(threadAction.ACTION_CHECK_KEYPRESSED)
        action.params_ = [elements, allEvents]

        # Add it as a sync action
        self._addAction(action, wait=True)
        return [False, None]

    # Wait for an event
    #
    def waitForEvent(self, elements, allEvents)  -> pygame.event.Event:
        # Create the action
        action = threadAction(threadAction.ACTION_WAIT_EVENT)
        action.params_ = [elements, allEvents]

        # Add it as a sync action
        self._addAction(action, wait=True)

        # unused
        return pygame.event.Event(0)

    #
    # Methods overloaded from pygameOutputs
    #

    # Draw window's background and grid's borders
    #
    def _drawBackground(self):
        self._addAction(id=threadAction.ACTION_DRAW_BKGRND)

    # Refresh the whole window
    #
    def _refresh(self, elements):
        action = threadAction(threadAction.ACTION_REFRESH)
        action.params_ = [elements, ""]
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
        self._start(self.position_)
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
            if True == self.newAction_.wait(1):
                # Do all the "actions"
                over, elements = self._handleActions(elements)

                # Wait for end of solving process ?
                while elements is not None:
                    self._int_draw(elements)
                    if True == self.newAction_.wait(0.1):
                        # Do all the "actions"
                        over, elements = self._handleActions(elements)
            else :
                # Any pygame event ?
                pygame.event.wait(1)

        # Finished !!!
        #print("Finished")

    #
    # "Internal" methods
    #

    # "Do" / perform the actions stored in the internal list
    #
    #   returns the tuple (thread should be ended ?, Grid if solving or None)
    #
    def _handleActions(self, elements): # noqa

        # Access to the list
        if False == self.accessList_.wait(MAX_THREAD_LIST_WAIT):
            # Impossible to access the list
            return (False, None)

        # Block list access
        self.accessList_.clear()

        # Transfer content to a working list
        workingList = []
        for action in self.actions_:
            workingList.append(action)

        # The list is freed (and empty)
        self.actions_.clear()

        # Allow other thread to add new actions
        self.newAction_.clear()
        self.accessList_.set()

        endThread = False

        for action in workingList:

            # Any drawings to do ?
            if elements is not None:
                self._int_draw(elements)

            match action.actionId_:
                case threadAction.ACTION_END_THREAD :
                    endThread = True

                case threadAction.ACTION_GRID_NAME :
                    self._int_setGridName(action.params_[0])

                case threadAction.ACTION_DRAW_TEXT :
                    self._int_displayText(action.params_[0], action.params_[1])

                case  threadAction.ACTION_DRAW_BKGRND :
                    self._int_drawBackground()

                case threadAction.ACTION_DRAW_GRID :
                    self._int_draw(action.params_[0])

                case threadAction.ACTION_DRAW_ELEMENT :
                    self._int_drawSingleElement(action.params_[0], action.params_[1], action.params_[2], action.params_[3], action.params_[4])

                case threadAction.ACTION_UPDATE :
                    self._int_update()

                case threadAction.ACTION_REFRESH | threadAction.ACTION_SOLVING_STARTED:
                   elements = action.params_[0]

                case threadAction.ACTION_SOLVING_ENDED :
                    elements = None

                case threadAction.ACTION_CHECK_KEYPRESSED :
                    ret = self._int_keyPressed(action.params_[0], action.params_[1])
                    if ret[0] :
                        self.syncRet_[action.uid_] = ret[1]

                case threadAction.ACTION_WAIT_EVENT :
                    self.syncRet_[action.uid_] = self._int_waitForEvent(action.params_[0], action.params_[1])

                case threadAction.ACTION_POLL_EVENT :
                    self.syncRet_[action.uid_] = self._int_pollEvent()

                case _ :
                    pass

            # Should I sync. ? (ie. should I notify the calling thread ?)
            if True == action.sync_:
                self.syncThreads_.set()

        return (endThread, elements)

# EOF
