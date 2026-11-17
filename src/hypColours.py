# coding=UTF-8
#
#   File        :   hypColours.py
#
#   Author      :   GeeHB
#
#   Description :   List of hypothesis colours
#

import element
import GUIStrings


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
        out:str = "hypColours ["

        added:bool = False
        for line in self.datas_:
            out+=f"({line[0]},{'empty' if line[1] is None else line[1]}),"
            added = True

        if added:
            out=out[:-1]
        out+="]"
        return out

    # Clear the list
    def clear(self):
        self.datas_.clear()

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
    def append(self, colID:element.hypColourID, pos:int | None = None)->bool:
        size:int = len(self)
        pop:bool = False
        if size > 1 and self.datas_[size-1][1] is None:
           self.pop()   # remove 'prev' colour is not used
           pop = True
        self.datas_.append((colID, pos))
        return not pop

    # Remove last element
    #
    # @return : position of last element if any or None
    #
    def pop(self)->int | None:
        if len(self.datas_)>0:
            return self.datas_.pop()[1]
        return None

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

    # Persistance
    #

    # Store list to temp file
    def toTemp(self)->str:
        out:str=""
        for col in self.datas_:
            out+=f"({col[0]}{GUIStrings.FILE_VALUE_SEPARATOR}{GUIStrings.STR_EMPTY if col[1] is None else col[1]}){GUIStrings.FILE_TEMP_DETAILS_SEP}"
        size:int = len(out)
        return "" if size <= 1  else out[:size-1]

    # Create a new list from temp
    #
    #  @return : True if successfully created
    #
    def fromTemp(self, line:str)->bool:
        if len(line) < 6 :
            return False

        hyps = line.split(GUIStrings.FILE_TEMP_DETAILS_SEP)
        if len(hyps) == 0:
            return False

        self.clear()
        for hyp in hyps:
            hyp = hyp.strip()
            if len(hyp) > 0 :
                choice = hyp[1:-1]
                res = choice.split(GUIStrings.FILE_VALUE_SEPARATOR)
                if len(res) == 2:
                    self.datas_.append(
                        (element.hypColourID(int(res[0])),
                            None if res[1] == GUIStrings.STR_EMPTY else int(res[1])
                        )
                    )

        return len(self.datas_) > 0

# EOF
