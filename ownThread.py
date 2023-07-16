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
MAX_LIST_WAIT = 5  # in sec.

# Actions
#
ACTION_NONE = 0  # Nothing to do


# Drawing action
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
ACTION_POLL_EVENT = 32

# Solving action

# End of the current thread
ACTION_END_THREAD = 999


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

    newAction_ = threading.Event()  # Notifies the thread a new action is to be performed
    accessList_ = threading.Event()  # Is action-list free ?
    syncThreads_ = threading.Event()  # Event for threads synchronisation

    # Start the thread 
    #
    def startThread(self):
        threading.Thread.__init__(self)  # Create the new thread
        self.start()  # start the thread (ie. call run() method )

    # End the thread
    def endThread(self):
        pass
# EOF