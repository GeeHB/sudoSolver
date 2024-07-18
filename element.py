# coding=UTF-8
#
#   File        :   element.py
#
#   Author      :   GeeHB
#
#   Description :   element object definition - a single sudoku element
#

#
# elementStatus - Element's status
#   It can be one or a combination of theses values
#
#class elementStatus(IntFlag):
class elementStatus(object):

    EMPTY = 0
    SET = 1
    OBVIOUS = 2         # An obvious value found at runtime (option -o / --obvious)
    ORIGINAL = 4        # Can't be changed (except in edition mode)


#
# element - a single sudoku element
#
class element(object):

    # Members
    #
    value_ = None                   # Num. value
    status_ = elementStatus.EMPTY   # Current status

    # Construction
    def __init__(self, value = None):
        if not value is None:
            # value is 'original'
            self.value_ = value
            self.status_ = elementStatus.ORIGINAL | elementStatus.SET

    # Set/modify the value
    #
    #           value : num. value (at this state the integrity is not checked)
    #           original : "original" value ? An "original" value won't be modified
    #
    def setValue(self, value = None, status = 0, editMode = False):
        if False == editMode :
            # The element can't be "original"
            if not self.status_ and elementStatus.ORIGINAL:
                # Update the value
                if not value is None:
                    self.value_ = value
                    self.status_ = elementStatus.SET

                    if 0 != status:
                        self.status_ |= status

                else:
                    self.status_ = elementStatus.EMPTY
        else:
            # Edition mode => value can be changed
            self.value_ = value
            self.status_ = elementStatus.EMPTY if 0 == self.value_ else elementStatus.SET | elementStatus.ORIGINAL

    def value(self):
        return self.value_ if self.status_ & elementStatus.SET else None

    # The element is empty
    #   returns the previous value
    def empty(self):
        self.status_ = elementStatus.EMPTY
        pValue = self.value_
        self.value_ = None      # Security issue ?
        return pValue

    # Element's status
    #
    def isEmpty(self):
        return self.status_ == elementStatus.EMPTY  # status is not set !

    def isOriginal(self):
        return ((self.status_ & elementStatus.ORIGINAL) == elementStatus.ORIGINAL)

    def isObvious(self):
        return self.__checkAttribute__(elementStatus.OBVIOUS)

    # At least can we modifiy this particular value ?
    def isChangeable(self):
        #return self.status_ <= elementStatus.SET    # just SET or EMPTY ?
        return self.status_ in [elementStatus.EMPTY, elementStatus.SET]

    # Internal meethods
    #

    # Check a single attribute
    def __checkAttribute__(self, attribute):
        return ((self.status_ & attribute) == attribute)

# EOF
