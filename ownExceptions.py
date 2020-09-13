# coding=UTF-8
#
#   File     :   ownExceptions.py
#
#   Author      :   JHB
#
#   Description :   Définition of exceptions objects  :
#                       - reachedEndOfList : A solution has been found
#                       - sudokuError : a bloking error
#
#   Remarque    :  
#
#   Version     :   0.1.25-2
#
#   Date        :   2020-09-13
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