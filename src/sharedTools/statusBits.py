# coding=UTF-8
#
#   File        :   statusBits.py
#
#   Author      :   GeeHB
#
#   Description :
#

STATUS_NONE = 0

# Bitwise operator wrapper
#
class statusBits(object):

    value_ = 0

    # Construction
    #
    def __init__(self, value = STATUS_NONE):
        self.value_ = value

    # Access
    #
    @property
    def value(self):
        return self.value_

    @value.setter
    def value(self, val):
        self.assign(val)

    def assign(self, value):
        self.value_ = value

    # Set a bit
    def set(self, bitVal):
        self.value_ |= bitVal

    # Unset/remove a bit
    def remove(self, bitVal):
        if self.isSet(bitVal):
            self.value_-=bitVal

    # Is a bit set ?
    def isSet(self, bitVal) -> bool:
        return False if bitVal == 0 else ((self.value_& bitVal) == bitVal)

# EOF
