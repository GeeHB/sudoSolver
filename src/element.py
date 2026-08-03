#!/usr/bin/env python
#
# coding=UTF-8
#
#   File        :   element.py
#
#   Author      :   GeeHB
#
#   Description :   element object definition - a single sudoku element
#

from sharedTools import statusBits


#
# element - a single sudoku element
#
class element:

    STATUS_EMPTY = 0
    STATUS_SET = 1
    STATUS_OBVIOUS = 2         # An obvious value found at runtime (option -o / --obvious)
    STATUS_ORIGINAL = 4        # Can't be changed (except in edition mode)

    # Members
    #
    value_ = None

    # Construction
    def __init__(self, value = None):
        if not value is None:
            self.value_ = value
            self.status_ = statusBits.statusBits(self.STATUS_ORIGINAL | self.STATUS_SET)

        self.status_ = statusBits.statusBits(self.STATUS_EMPTY)   # Current status

    # element's value as a property
    #
    @property
    def num(self):
        return self.value_ if self.status_.isSet(self.STATUS_SET) else None
    @num.setter
    def num(self, newVal):
        self.value_ = newVal

    # Set/modify the value
    #
    #           value : num. value (at this state the integrity is not checked)
    #           original : "original" value ? An "original" value won't be modified
    #
    def setValue(self, value = None, status = 0, editMode = False):
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
            self.value_ = value
            self.status_.assign(self.STATUS_EMPTY if 0 == self.value_ else self.STATUS_SET | self.STATUS_ORIGINAL)

    def value(self):
        return self.value_ if self.status_.isSet(self.STATUS_SET) else None

    # The element is empty
    #   returns the previous value
    def empty(self):
        self.status_.assign(self.STATUS_EMPTY)
        pValue = self.value_
        self.value_ = None      # Security issue ?
        return pValue

    # Element's status
    #
    def isEmpty(self):
        return self.status_.value == self.STATUS_EMPTY  # status is not set !

    def isOriginal(self):
        return self.status_.isSet(self.STATUS_ORIGINAL)
    def setOriginal(self):
        self.status_.assign(self.STATUS_SET | self.STATUS_ORIGINAL)

    def isObvious(self):
        return self.status_.isSet(self.STATUS_OBVIOUS)

    # At least can we modifiy this particular value ?
    def isChangeable(self):
        #return self.status_ <= self.STATUS_SET    # just SET or EMPTY ?
        return self.status_.value in [self.STATUS_EMPTY, self.STATUS_SET]
# EOF
