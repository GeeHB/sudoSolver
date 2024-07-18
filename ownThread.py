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

# Actions
#
ACTION_NONE = 0         # Nothing to do

ACTION_END_THREAD = 999 # End of the current thread

#
# for PYGame
#

# Drawing action
ACTION_DRAW_BKGRND = 1
ACTION_DRAW_GRID = 2
ACTION_DRAW_ELEMENT = 3
ACTION_DRAW_TEXT = 4
ACTION_GRID_NAME = 5
ACTION_GRID_FROM_FILE = 6

ACTION_UPDATE = 10
ACTION_REFRESH = 11

# Solving actions
ACTION_SOLVING_STARTED = 20
ACTION_SOLVING_ENDED = 21

# Events management
ACTION_CHECK_KEYPRESSED = 30  # Sync event
ACTION_WAIT_EVENT = 31
ACTION_POLL_EVENT = 32

#
# threadAction : Single action
#
class threadAction(object):
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
# Thread object
#
class Thread(threading.Thread):
    # Members
    #
    ready_ = False  # Am I ready ?
    actions_ = []  # Actions (to perform)

    syncRet_ = {}  # Returns from a sync-action
    lastId_ = 0

    newAction_ = threading.Event()      # Notifies the thread a new action is to be performed
    accessList_ = threading.Event()     # Is action-list free ?
    syncThreads_ = threading.Event()    # Event for threads synchronisation

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
    def _addAction(self, action=None, id=None, wait=False):

        # Action or id must be present
        if action is None and id is None:
            return False

        # Valid action id ?
        if (action != None and action.actionId_ == ACTION_NONE) or (
                action is None and id == ACTION_NONE) or False == self.accessList_.wait(MAX_THREAD_LIST_WAIT):
            return False

        # Take list ownership
        self.accessList_.clear()

        # Add new action to the list
        if action is None:
            action =  threadAction(id if id is not None else ACTION_NONE)

        # Should I sync both threads ?
        if action is not None:
            action.sync_ = wait

        # Wait for action completion ?
        if True == wait:
            self.syncThreads_.clear()  # Should be useless !

        # Add to list (with uid)
        self.lastId_ = self.lastId_ + 1
        if action is not None :
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
                    return self.syncRet_[action.uid_] if action is not None else False
                except:
                    return False

        # Done
        return True
# EOF
