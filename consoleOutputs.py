# coding=UTF-8
#
#   File        :   consoleOutputs.py
#
#   Author      :   GeeHB
#
#   Description :   consoleOutputs object - Display the sudoku's grid on a console
#

from outputs import outputs
from pointer import LINE_COUNT, ROW_COUNT

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
        for _ in range(LINE_COUNT):
            line = ""
            myCol = 0
            for _ in range(ROW_COUNT):
                currentElement = elements[myIndex]
                line+=" "
                line+= " " if currentElement.isEmpty() else str(currentElement.value())
                line+=" "
                myIndex += 1

                # Change tiny-square
                myCol += 1
                if 3 == myCol:
                    line += " "
                    myCol = 0
            
            # EOL
            print(line)
            myLine += 1
            if 3 == myLine:
                # empty line between tiny-squares
                myLine = 0
                print("")
 
 # EOF