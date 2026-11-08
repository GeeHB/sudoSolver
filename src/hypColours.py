# coding=UTF-8
#
#   File        :   hypColours.py
#
#   Author      :   GeeHB
#
#   Description :   List of hypothesis colours
#

import element
import pointer


# List of used hyp. colours
#
class hypColours:
    # Construction
    def __init__(self):
        self.datas_ : list[tuple[element.hypColourID, pointer.pointer | None]] = []

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

    # Append an element
    def append(self, colID:element.hypColourID):
        self.datas_.append((colID, None))

    # Remove last element
    def pop(self):
        if len(self.datas_)>0:
            self.datas_.pop()

    # Access
    def setPositionAt(self, where:int, pos:pointer.pointer)->bool:
        if where>=0 and where < len(self.datas_):
            self.datas_[where] = (self.datas_[where][0], pos)
            return True
        return False    # not modified

    # Get a colID by index
    def getColIDAt(self, where:int)->element.hypColourID:
        return self.datas_[where][0] if where>=0 and where < len(self.datas_) else element.hypColourID.NO_COLOUR # Invalid index

    # Get a copy of indexed values
    def getAt(self, where:int)->tuple[element.hypColourID, pointer.pointer | None] | None:
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
