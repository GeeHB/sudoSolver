# coding=UTF-8
#
#   File        :   element.py
#
#   Author      :   GeeHB
#
#   Description :   element object definition - a single sudoku element
#

from enum import IntEnum, auto

from typing_extensions import override

from sharedTools import statusbits


# Tag/hypothesis colours
#
class hypColourID(IntEnum):
    NO_HYP = 0
    HYP_1 = auto()
    HYP_2 = auto()
    HYP_3 = auto()
    HYP_4 = auto()

# Element's status
#
class elementStatus(IntEnum):
    STATUS_EMPTY        = 0
    STATUS_SET          = 1
    STATUS_OBVIOUS      = 2     # An obvious value found at runtime (option -o / --obvious)
    STATUS_ORIGINAL     = 4     # Can't be changed (except in edition mode)
    STATUS_NOTIFYING    = 8     # The current element is notifying the user (creation, help, obvious value, mistake, ...)
    STATUS_ERROR        = 16    # The value is invalid and the element is shown as an error

# element - a single sudoku element
#
class element:
    # Construction
    def __init__(self, value:int | None = None):
        self.value_:int = 0;
        self.solution_:int | None = None
        self.hyp_:int = hypColourID.NO_HYP

        if not value is None:
            self.value_ = value
            self.status_:statusbits.statusBits = statusbits.statusBits(elementStatus.STATUS_ORIGINAL | elementStatus.STATUS_SET)
        else:
            self.status_ = statusbits.statusBits(elementStatus.STATUS_EMPTY)   # Current status

    # Representation
    @override
    def __repr__(self) -> str:
        out : str = "Element:"
        out += f"\n\t - {"Invalid" if self.isInvalid() else "Valid"}"
        out += f"\n\t- Status : {self.status_.value_}"
        out += f"\n\t- Value : {"empty" if self.status_.isSet(elementStatus.STATUS_EMPTY) else self.value_}"
        if self.solution_ is not None:
            out += f"\n\t- Solution : {self.solution_}"
        return out

    # element's value as a property
    #
    @property
    def num(self)->int | None:
        return self.value_ if self.status_.isSet(elementStatus.STATUS_SET) else None
    @num.setter
    def num(self, newVal : int | None):
        if newVal is not None and newVal > 0:
            self.value_ = newVal
        else:
            self.status_.assign(elementStatus.STATUS_EMPTY)

    # element's "valid" value as a property
    #
    @property
    def solution(self)->int | None:
        return self.solution_
    @solution.setter
    def solution(self, newVal : int | None):
        self.solution_ = newVal

    # 'show'/set the solution for the given element
    def revealSolution(self):
        if self.solution_ is not None:
            self.value_ = self.solution_
            self.status_.set(elementStatus.STATUS_SET | elementStatus.STATUS_NOTIFYING)

    # show the element as an error
    #
    @property
    def error(self)->bool:
        return self.status_.isSet(elementStatus.STATUS_ERROR)
    @error.setter
    def error(self, show:bool):
        self.status_.set(elementStatus.STATUS_ERROR | elementStatus.STATUS_NOTIFYING, show and self.isInvalid())

    # In the notifying state ?
    #
    @property
    def notifying(self)->bool:
        return self.status_.isSet(elementStatus.STATUS_NOTIFYING)
    @notifying.setter
    def notifying(self, set:bool):
        self.status_.set(elementStatus.STATUS_NOTIFYING, set)

    # hypothesis's colour ID
    #
    @property
    def hypothesis(self)->int:
        return self.hyp_
    @hypothesis.setter
    def hypothesis(self, newVal : int):
        if newVal >= hypColourID.NO_HYP and newVal <= hypColourID.HYP_4:
            self.hyp_ = newVal

    # Set/modify the value
    #
    #           value : num. value (at this state the integrity is not checked)
    #           original : "original" value ? An "original" value won't be modified
    #
    def setValue(self, value:int | None = None, status:int = elementStatus.STATUS_EMPTY, editMode:bool = False):
        if not editMode :
            # The element can't be "original"
            if not self.status_.isSet(elementStatus.STATUS_ORIGINAL):
                # Update the value
                if value is not None:
                    self.value_ = value
                    self.status_.assign(elementStatus.STATUS_SET)

                    if 0 != status:
                        self.status_.set(status)
                else:
                    self.value_ = 0
                    self.status_.assign(elementStatus.STATUS_EMPTY)
        else:
            # Edition mode => value can be changed
            if value is None or value == 0:
                self.value_ = 0
                self.status_.assign(elementStatus.STATUS_EMPTY)
            else :
                self.value_ = value
                self.solution_ = value
                self.status_.assign(elementStatus.STATUS_SET | elementStatus.STATUS_ORIGINAL)

    # Empty the element
    #   returns the previous value
    def empty(self, deep : bool):
        self.status_.assign(elementStatus.STATUS_EMPTY)
        pValue = self.value_
        self.value_ = 0
        if deep:
            self.solution_ = 0
        self.hyp_ = hypColourID.NO_HYP
        return pValue

    # Element's status
    #
    def hasValue(self)->bool:
        return self.status_.isSet(elementStatus.STATUS_SET) and self.value_ != 0

    def isInvalid(self)->bool:
        return not self.isOriginal() and self.hasValue() and self.value_ != self.solution

    def isEmpty(self)->bool:
        return self.status_.value == elementStatus.STATUS_EMPTY  # status is not set !

    def isOriginal(self)->bool:
        return self.status_.isSet(elementStatus.STATUS_ORIGINAL)
    def setOriginal(self):
        self.status_.assign(elementStatus.STATUS_SET | elementStatus.STATUS_ORIGINAL)
        self.solution_ = self.value_

    def isObvious(self)->bool:
        return self.status_.isSet(elementStatus.STATUS_OBVIOUS)

    # At least can we modifiy or set this element ?
    def isChangeable(self, allowEmpty:bool = True)->bool:
        return not self.status_.isSet(elementStatus.STATUS_ORIGINAL) if allowEmpty else (self.isObvious() or self.status_.value == elementStatus.STATUS_SET)

# EOF
