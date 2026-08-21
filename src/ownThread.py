#!/usr/bin/env python
#
# coding=UTF-8
#
#   File        :   ownThread.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of Thread and threadAction objects
#                   Atomic action to perform by a thread
#

import threading

#
# Internal constants
#

# Wait for list availability
MAX_THREAD_LIST_WAIT = 5  # in sec.

#
# threadAction : Single action
#
class threadAction:

    # Actions
    #
    ACTION_NONE:int = 0         # Nothing to do

    ACTION_END_THREAD:int = 999 # End of the current thread

    #
    # for PYGame
    #

    # Drawing action
    ACTION_DRAW_BKGRND:int = 1
    ACTION_DRAW_GRID:int = 2
    ACTION_DRAW_ELEMENT:int = 3
    ACTION_DRAW_TEXT:int = 4
    ACTION_GRID_NAME:int = 5
    ACTION_GRID_FROM_FILE:int = 6

    ACTION_UPDATE:int = 10
    ACTION_REFRESH:int = 11

    # Solving actions
    ACTION_SOLVING_STARTED:int = 20
    ACTION_SOLVING_ENDED:int = 21

    # Events management
    ACTION_CHECK_KEYPRESSED:int = 30  # Sync event
    ACTION_WAIT_EVENT:int = 31
    ACTION_POLL_EVENT:int = 32

    # Construction
    def __init__(self, id:int = ACTION_NONE):
        self.uid_:int = 0
        self.actionId_:int = id
        self.sync_:bool = False  # Synchronized with the calling thread ?
        self.params_:list[int] = []  # Optionnal parameters (depends on action)

#
# Thread object
#
class Thread(threading.Thread):
    # Construction
    def __init__(self):
        super.__init__()

        self.ready_:bool = False  # Am I ready ?
        self.actions_ = []  # Actions (to perform)
        self.syncRet_ = {}  # Returns from a sync-action
        self.lastId_:int = 0
        self.newAction_ = threading.Event()      # Notifies the thread a new action is to be performed
        self.accessList_ = threading.Event()     # Is action-list free ?
        self.syncThreads_ = threading.Event()    # Event for threads synchronisation

    # Start the thread
    def initiate(self):
        threading.Thread.__init__(self)  # Create the new thread
        self.start()  # start the thread (ie. call run() method )

    # Terminate the thread
    def terminate(self):
        pass

    #
    # "Internal" methods
    #

    # Add an action to the internal list
    #
    def _addAction(self, action:threadAction | None = None, id:int | None=None, wait:bool=False) -> bool:

        # Action or id must be present
        if action is None and id is None:
            return False

        # Valid action id ?
        if (action is not None and action.actionId_ == threadAction.ACTION_NONE) or (
                action is None and id == threadAction.ACTION_NONE) or False == self.accessList_.wait(MAX_THREAD_LIST_WAIT):
            return False

        # Take list ownership
        self.accessList_.clear()

        # Add new action to the list
        if action is None:
            action =  threadAction(id if id is not None else threadAction.ACTION_NONE)

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
        if wait and action.actionId_ != threadAction.ACTION_END_THREAD:
            self.syncThreads_.wait()

            # done ...
            self.syncThreads_.clear()

            # handle return
            try:
                return self.syncRet_[action.uid_] if action is not None else False
            except:
                return False

        # Done
        return True
# EOF
