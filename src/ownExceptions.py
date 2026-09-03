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

from typing import override


#
# reachedEndOfList : End of resolution mode
#
class reachedEndOfList(Exception):
    pass

#
# sudokuError : An error ...
#
class sudokuError(Exception):
    def __init__(self, message:str):
        self.message_ : str = message
        super().__init__(self.message_)

    @override
    def __str__(self)->str:
        return self.message_

    @override
    def __repr__(self)->str:
        return f"sudokuError : {self.message_}"

# EOF
