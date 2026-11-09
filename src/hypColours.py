# coding=UTF-8
#
#   File        :   hypColours.py
#
#   Author      :   GeeHB
#
#   Description :   List of hypothesis colours
#

import element


# List of used hyp. colours
#
class hypColours:
    # Construction
    def __init__(self):
        self.datas_ : list[tuple[element.hypColourID, int | None]] = []

    # Size
    def __len__(self)->int:
        return len(self.datas_)

    # Representation
    def __repr__(self)->str:
        out:str = "["
        for line in self.datas_:
            out+=f"({line[0]}, {'empty' if line[1] is None else line[1]}),"
        out+="]"
        return out

    # Search colour by ID
    def getIndex(self, colID:int)->int:
        for index in range(len(self.datas_)):
            if self.datas_[index][0] == colID:
               return index
        return -1   # not found

    # Append a colour to the list
    #
    #  @return : True if the colour has been added
    #
    def append(self, colID:element.hypColourID, position:int | None = None)->bool:
        size:int = len(self)
        pop:bool = False
        if size > 1 and self.datas_[size-1][1] is None:
           self.pop()   # remove 'prev' colour is not used
           pop = True
        self.datas_.append((colID, position))
        return not pop

    # Remove last element
    def pop(self):
        if len(self.datas_)>0:
            self.datas_.pop()

    # Set position of first element using the current colour
    def setFirstPosition(self, pos:int)->bool:
        where:int = len(self.datas_) - 1
        if where > 0 and self.datas_[where][1] is None:
            self.datas_[where] = (self.datas_[where][0], pos)   # only if not already set
            return True
        return False    # not modified

    # Get a colID by index
    def getColIDAt(self, where:int)->element.hypColourID:
        return self.datas_[where][0] if where>=0 and where < len(self.datas_) else element.hypColourID.NO_HYP # Invalid index

    # Get a copy of indexed values
    def getAt(self, where:int)->tuple[element.hypColourID, int | None] | None:
        if where>=0 and where < len(self.datas_):
            return self.datas_[where]
        return None # Invalid index

    # Get the list of colours' ids
    def toList(self)->list[element.hypColourID]:
        lst:list[element.hypColourID] = []
        for line in self.datas_:
            lst.append(line[0])
        return lst

# EOF
