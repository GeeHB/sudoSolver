# coding=UTF-8
#
#   File        :   drawThread.py
#
#   Author      :   JHB
#
#   Description :   Thread used for drawing the grid (PYGame only)
#
#   Version     :   1.3.1
#
#   Date        :   2021-08-02
#

import threading
import pygameOutputs

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
        self.over_ = False

    # Where all the stuff is done
    def run(self):
        
        # Check wether PYGame is used or not
        if type(self.outputs_) is pygameOutputs.pygameOutputs :
            # Yes !!!    
        
            # Keep on drawing the grid's elements
            while not self.over_:
                self.outputs_.draw(self.elements_)

            # until it's over ...

    # Stop the thread
    def stop(self):
        self.over_ = True

# EOF