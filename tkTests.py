# coding=UTF-8
#
#   File        :   tkTests.py
#
#   Author      :   GeeHB
#
#   Description :   TCL/TK tests
#

import tkinter as tk

window = tk.Tk()
window.title = "Console"
greeting = tk.Label(text="Hello, Tkinter")
greeting.pack()
window.mainloop()

# EOF