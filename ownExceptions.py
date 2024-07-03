# coding=UTF-8
#
#   File        :   ownExceptions.py
#
#   Author      :   GeeHB
#
#   Description :   Définition of exceptions objects  :
#                       - reachedEndOfList : A solution has been found
#                       - sudokuError : a bloking error
#

#
# reachedEndOfList : End of resolution mode
#
class reachedEndOfList(Exception):
    pass

#
# sudokuError : An error ...
#
class sudokuError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message

# EOF