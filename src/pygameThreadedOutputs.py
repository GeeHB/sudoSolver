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
from typing import override

import pygame.event

from element import element
from ownThread import (
    MAX_THREAD_LIST_WAIT,
    Thread,
    threadAction,
)
from pygameOutputs import pygameOutputs


#
# pygameThreadedOutputs - Display sudoku's grid using PYGame library
#
class pygameThreadedOutputs(pygameOutputs, Thread):

    # Construction
    #
    def __init__(self, position : tuple[int,int] | None = None):

        self.position_ = position

        # Start the current thread
        super().initiate()

    #
    # Methods overloaded from outputs
    #

    # Ready to go ?
    @override
    def isReady(self) -> bool:
        return self.ready_

    # Display text
    #
    @override
    def displayText(self, text : str, information : bool, elements : list[element]):
        if information:
            super().displayText(text, True, elements)
        else:
            action = threadAction(threadAction.ACTION_DRAW_TEXT)
            action.params_ = [text, elements]
            self._addAction(action)

    # Set/change the current grid's filename
    #   overloaded
    def setGridName(self, fileName:str, create:bool = False):
        action = threadAction(threadAction.ACTION_GRID_NAME)
        action.params_ = [fileName, ""]

        self._addAction(action)

    # Draw the whole grid
    #
    def draw(self, elements:list[element]):
        action = threadAction(threadAction.ACTION_DRAW_GRID)
        action.params_ = [elements, ""]
        self._addAction(action)

    # Draw/erase a single element and its background
    #
    def drawSingleElement(self, row:int, line:int, value:int, bkColour:pygame.Color, txtColour:pygame.Color):

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
    @override
    def update(self):
        self._addAction(id=threadAction.ACTION_UPDATE)

    # Start of solving process
    #   can be overloaded
    def startedSolving(self, elements:list[element]):
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
    def pollEvent(self, elements:list[element] | None =None, allEvents:bool = False)  -> pygame.event.Event:
        # Create the action
        action = threadAction(threadAction.ACTION_POLL_EVENT)
        action.params_ = [elements, allEvents]

        # Add it as a sync action
        self._addAction(action, wait=True)
        return pygame.event.Event(0)

    # Is a key pressed ?
    #
    #   returns the tuple (pressed?, key or None if not pressed)
    #
    @override
    def keyPressed(self, elements : list[element] | None = None, allEvents:bool=False)->tuple[bool,pygame.event.Event | None]:
        # Create the action
        action = threadAction(threadAction.ACTION_CHECK_KEYPRESSED)
        action.params_ = [elements, allEvents]

        # Add it as a sync action
        self._addAction(action, wait=True)
        return (False, None)

    # Wait for an event
    #
    def waitForEvent(self, elements : list[element], allEvents : bool)  -> pygame.event.Event:
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
    def drawBackground(self):
        self._addAction(id=threadAction.ACTION_DRAW_BKGRND)

    # Refresh the whole window
    #
    @override
    def _refresh(self, elements : list[element] | None):
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
        elements : list[element] | None = None

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
    def _handleActions(self, elements:list[element] | None)->tuple[bool, list[element] | None]:
        retElements : bool = True
        endThread : bool = False

        if elements is not None :
            # Access to the list
            if False == self.accessList_.wait(MAX_THREAD_LIST_WAIT):
                # Impossible to access the list
                return (False, None)

            # Block list access
            self.accessList_.clear()

            # Transfer content to a working list
            workingList = self.actions_.copy()

            # The list is freed (and empty)
            self.actions_.clear()

            # Allow other thread to add new actions
            self.newAction_.clear()
            self.accessList_.set()


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
                        retElements = False

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

        return (endThread, elements if retElements else None)

# EOF
