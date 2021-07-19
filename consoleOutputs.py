# coding=UTF-8
#
#   File     :   consoleOutputs.py
#
#   Author      :   JHB
#
#   Description :   consoleOutputs object - Display the sudoku's grid on a console
#
#   Version     :   1.1.2
#
#   Date        :   2021-07-19
#
from outputs import outputs
from element import element, elementStatus
from pointer import pointer

#
# consoleOutputs - Basic display in console mode
#
class consoleOutputs(outputs):
    
    # Draw the grid
    #
    def draw(self, elements):
        
        myIndex = 0
        myLine = 0

        print("")

        # Draw line / line
        #
        for _ in range(pointer.LINE_COUNT):
            line = ""
            myCol = 0
            for _ in range(pointer.ROW_COUNT):
                currentElement = elements[myIndex]
                line+=" "
                line+= " " if currentElement.isEmpty() else str(currentElement.value())
                line+=" "
                myIndex += 1

                # Change "small square"
                myCol += 1
                if 3 == myCol:
                    line += " "
                    myCol = 0
            
            # EOL
            print(line)
            myLine += 1
            if 3 == myLine:
                # empty line between "small" squares
                myLine = 0
                print("")
 
 # EOF