# coding=UTF-8
#
#   File        :   element.py
#
#   Author      :   GeeHB
#
#   Description :   element object definition - a single sudoku element
#

from typing_extensions import override

from sharedTools import statusbits


#
# element - a single sudoku element
#
class element:
    STATUS_EMPTY: int = 0
    STATUS_SET: int  = 1
    STATUS_OBVIOUS: int  = 2         # An obvious value found at runtime (option -o / --obvious)
    STATUS_ORIGINAL: int  = 4        # Can't be changed (except in edition mode)

    # Construction
    def __init__(self, value:int | None = None):
        self.value_: int = 0;
        self.solution_ : int | None = None
        if not value is None:
            self.value_ = value
            self.status_:statusbits.statusBits = statusbits.statusBits(self.STATUS_ORIGINAL | self.STATUS_SET)
        else:
            self.status_ = statusbits.statusBits(self.STATUS_EMPTY)   # Current status

    # Representation
    @override
    def __repr__(self) -> str:
        out : str = "Element:"
        out += f"\t\n- Status : {self.status_}"
        out += f"\n\t- Value : {"empty" if self.status_.isSet(self.STATUS_EMPTY) else self.value_}"
        if self.solution_ is not None:
            out += f"\n\t- Solution : {self.solution_}"
        return out

    # element's value as a property
    #
    @property
    def num(self)->int | None:
        return self.value_ if self.status_.isSet(self.STATUS_SET) else None
    @num.setter
    def num(self, newVal : int | None):
        if newVal is not None:
            self.value_ = newVal
        else:
            self.status_.assign(self.STATUS_EMPTY)

    # element's "valid" value as a property
    #
    @property
    def solution(self)->int | None:
        return self.solution_
    @solution.setter
    def solution(self, newVal : int | None):
        self.solution_ = newVal

    # Set/modify the value
    #
    #           value : num. value (at this state the integrity is not checked)
    #           original : "original" value ? An "original" value won't be modified
    #
    def setValue(self, value:int | None = None, status:int = STATUS_EMPTY, editMode:bool = False):
        if not editMode :
            # The element can't be "original"
            if not self.status_.isSet(self.STATUS_ORIGINAL):
                # Update the value
                if not value is None:
                    self.value_ = value
                    self.status_.assign(self.STATUS_SET)

                    if 0 != status:
                        self.status_.set(status)

                else:
                    self.status_.assign(self.STATUS_EMPTY)
        else:
            # Edition mode => value can be changed
            if value is None or value == 0:
                self.value_ = 0
                self.status_.assign(self.STATUS_EMPTY)
            else :
                self.value_ = value
                self.solution_ = value
                self.status_.assign(self.STATUS_SET | self.STATUS_ORIGINAL)

    # The element is empty
    #   returns the previous value
    def empty(self):
        self.status_.assign(self.STATUS_EMPTY)
        pValue = self.value_
        self.value_ = 0
        return pValue

    # Element's status
    #
    def isEmpty(self)->bool:
        return self.status_.value == self.STATUS_EMPTY  # status is not set !

    def isOriginal(self)->bool:
        return self.status_.isSet(self.STATUS_ORIGINAL)
    def setOriginal(self):
        self.status_.assign(self.STATUS_SET | self.STATUS_ORIGINAL)

    def isObvious(self)->bool:
        return self.status_.isSet(self.STATUS_OBVIOUS)

    # At least can we modifiy this particular value ?
    def isChangeable(self)->bool:
        #return self.status_ <= self.STATUS_SET    # just SET or EMPTY ?
        return self.status_.value in [self.STATUS_EMPTY, self.STATUS_SET]
# EOF
