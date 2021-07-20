#!/usr/bin/env python3

# coding=UTF-8
#
#   File        :   drawThread.py
#
#   Author      :   JHB
#
#   Description :   Thread used for drawing the grid (PYGame only)
#
#   Version     :   1.2.2
#
#   Date        :   2021-07-20
#

import threading
from outputs import outputs
import pygameOutputs
#import element

#
#   drawThread object : Draw the grid during search process
#
class drawThread(threading.Thread):
    # Construction
    def __init__(self, gridOutputs, elements):
        threading.Thread.__init__(self)
        
        # Initialize members
        self.outputs_ = gridOutputs
        self.elements_ = elements
        self.done_ = False

    # Where all the stuff is done
    def run(self):
        
        # Check wether PYGame is used or not
        if type(self.outputs_) is pygameOutputs.pygameOutputs :
            # Yes !!!    
        
            # Keep on drawing the grid's elements
            while not self.done_:
                self.outputs_.draw(self.elements_)

    # Stop the thread ...
    def stop(self):
        self.done_ = True

# EOF