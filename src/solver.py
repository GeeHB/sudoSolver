# coding=UTF-8
#
#   File        :   sudoku.py
#
#   Author      :   GeeHB
#
#   Description :   solver object
#                       - abstract class
#

from options import options
from sArray import sArray


class solver:
    def __init__(self, params : options):
        self.params_ : options = params
        self.sudoku_ : sArray = sArray()    # First empty array

    def initialize(self):
        pass

    def start(self):
        pass


# EOF
