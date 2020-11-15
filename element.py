# coding=UTF-8
#
#   File     :   element.py
#
#   Author      :   JHB
#
#   Description :   element object definition - a single sudoku element
#
#   Version     :   0.1.27
#
#   Date        :   2020-11-15
#

#
# elementStatus - Element's status
#
class elementStatus(object):

    EMPTY = 0
    SET = 1
    VALUED = 1
    ORIGINAL = 2        # Can't be changed (except on edition mode)

#
# element - a single sudoku element
#
class element(object):

    # Members
    #
    value_ = None                   # Num. value
    status_ = elementStatus.EMPTY   # Current state

    # Construction
    def __init__(self, value = None):
        if not None == value:
            # value is 'original'
            self.value_ = value
            self.status_ = elementStatus.ORIGINAL | elementStatus.SET

    # Set/modify the value
    #
    #           value : num. value (at this state the integrity is not checked)
    #           original : "original" value ? An "original" value won't be modified
    #
    def setValue(self, value = None, original = False, editMode = False):
        if False == editMode :
            # The element can't be "original"
            if not self.status_ and elementStatus.ORIGINAL:
                # Update the value
                if not value == None:
                    self.value_ = value
                    self.status_ = elementStatus.SET

                    if True == original:
                        self.status_ |= elementStatus.ORIGINAL

                else:
                    self.status_ = elementStatus.EMPTY
        else:
            # Edition mode => value can be changed
            self.value_ = value
            self.status_ = elementStatus.EMPTY if 0 == self.value_ else elementStatus.SET | elementStatus.ORIGINAL

    def value(self):
        return self.value_ if self.status_ & elementStatus.SET else None

    # The element is empty
    #   returns previous value
    def  empty(self):
        self.status_ = elementStatus.EMPTY
        return self.value_

    # Element's status
    #
    def isEmpty(self):
        return self.status_ == elementStatus.EMPTY
    
    def isOriginal(self):
        return ((self.status_ & elementStatus.ORIGINAL) == elementStatus.ORIGINAL)

# EOF