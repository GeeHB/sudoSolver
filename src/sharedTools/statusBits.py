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
class statusBits:

    # Construction
    #
    def __init__(self, value: int = STATUS_NONE):
        self.value_: int = value

    # Access
    #
    @property
    def value(self):
        return self.value_

    @value.setter
    def value(self, val : int):
        self.assign(val)

    def assign(self, value: int):
        self.value_ = value

    # Set a bit
    def set(self, bitVal: int):
        self.value_ |= bitVal

    # Unset/remove a bit
    def remove(self, bitVal: int):
        if self.isSet(bitVal):
            self.value_-=bitVal

    # Is a bit set ?
    def isSet(self, bitVal:int) -> bool:
        return False if bitVal == 0 else ((self.value_& bitVal) == bitVal)

# EOF
