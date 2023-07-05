#!/usr/bin/python3
#
# coding=UTF-8
#
#   File        :   tksudoSolver.py
#
#   Author      :   GeeHB
#
#   Description :   Edit & solve sudokus
#                   with GUI using tkinter
#

from ownExceptions import sudokuError

try:
    import tkinter as tk                    
    from tkinter import ttk
    import tkinter.font as tkFont
except ModuleNotFoundError:
    raise sudokuError("tkinter module is not installed")

import os

import options as opts
from sudoku import sudoku

# Main window handling app's parameters
# 
class sudoParamWindow(tk.Tk):

    # Construction
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fileName_ = None
        self.config(width=opts.APP_GUI_WITH, height=opts.APP_GUI_HEIGHT)
        self.title(opts.APP_GUI_TITLE)

        # members' values
        self.files_ = []

        # my sudoku solver
        self.solver_ = sudoku(progressMode=opts.options.PROGRESS_SINGLETHREADED)

        # Change the default font ...
        self.ownFont_ = tkFont.nametofont("TkDefaultFont")
        self.ownFont_.configure(family="Arial", weight="normal", size=11)
        #root.option_add("*Font", default_font)

        # Tab manager ...
        self.tabControl_ = ttk.Notebook(self) 

        # ... with 2 tabs
        self.gridsTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.gridsTab_, text = opts.APP_GUI_TAB_GRIDS)
        
        self.solveTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.solveTab_, text = opts.APP_GUI_TAB_SOLVE)

        self.tabControl_.pack(expand = 1, fill ="both")
        
        # "Grids" tab
        #

        # Folder name
        ttk.Label(self.gridsTab_, text = 'Folder name :').grid(column=0, row=0, padx=5, pady=5)
        
        self.folderNameEdit_ = ttk.Entry(self.gridsTab_)
        self.folderNameEdit_.grid(column=1, row=0, columnspan=3, padx=5, pady=5)

        #self.folderNameEdit_.configure(font=self.ownFont_)
        
        self.folderBrowseButton_ = ttk.Button(self.gridsTab_, text='Browse')
        self.folderBrowseButton_.grid(column=5, row=0, padx=5, pady=5)

        # File name
        ttk.Label(self.gridsTab_, text = 'File name :').grid(column=0, row=1, padx=5, pady=5)

        self.fileNameEdit_ = ttk.Entry(self.gridsTab_)
        self.fileNameEdit_.grid(column=1, row=1, columnspan=3, padx=5, pady=5)

        # "walk" buttons
        self.folderPrevButton_ = ttk.Button(self.gridsTab_, text='<<', command = self._prevFile, state = tk.DISABLED)
        self.folderPrevButton_.grid(column=1, row=2, padx=5, pady=5)

        self.folderNextButton_ = ttk.Button(self.gridsTab_, text='>>', command = self._nextFile, state = tk.DISABLED)
        self.folderNextButton_.grid(column=2, row=2, padx=5, pady=5)

        # File control buttons
        self.fileCreateButton_ = ttk.Button(self.gridsTab_, text='Create')
        self.fileCreateButton_.grid(column=0, row=3, padx=5, pady=25)

        self.fileEditButton_ = ttk.Button(self.gridsTab_, text='Edit', state = tk.DISABLED)
        self.fileEditButton_.grid(column=1, row=3, padx=5, pady=25)

        # "Solve" tab
        #
        self.obviousValuesButton_ = ttk.Button(self.solveTab_, text='Search obvious values', command = self._obviousValues, state = tk.DISABLED)
        self.obviousValuesButton_.grid(column=0, row=0, columnspan=2, sticky = 'w', padx=5, pady=5)

        ttk.Label(self.solveTab_, text = "Show progress :").grid(column=0, row=1, padx=5, pady=5)
        self.progressMode_ = tk.StringVar()
        self.progressCombo_ = ttk.Combobox(self.solveTab_, textvariable=self.progressMode_, state = 'readonly')
        self.progressCombo_.grid(column=1, row=1, padx=5, pady=5)
        self.progressCombo_['values'] = ('none', 'slow', 'multithreaded')
        self.progressCombo_.current(1)  # show progress slowly 

        # Buttons
        self.solveButton_ = ttk.Button(self.solveTab_, text='Solve', command = self._solve, state = tk.DISABLED)
        self.solveButton_.grid(column=0, row=3, sticky = 'w', padx=5, pady=25)

        self.saveButton_ = ttk.Button(self.solveTab_, text='Save', state = tk.DISABLED)
        self.saveButton_.grid(column=1, row=3, sticky = 'w', padx=5, pady=25)

        # Default values
        self.fileName = ""
        self.folderName = opts.DEF_FOLDER

    # Folder name
    @property
    def folderName(self):
        return self.folderNameEdit_.get()
    
    @folderName.setter
    def folderName(self, value):
        if value is None :
            value = ""

        # Value changed ?
        if self.folderName == value :
            # Nothing to do
            return
        
        # The folder exists ?
        val = "" if value is None or False == os.path.isdir(value) else value
        self.folderNameEdit_.delete(0,tk.END)
        self.folderNameEdit_.insert(0,val)

        self.fileIndex_ = 0

        if False == self.solver_.folderContent(value, self.files_) :
            # No files in the list => no browse ...
            self.folderPrevButton_["state"] = tk.DISABLED
            self.folderNextButton_["state"] = tk.DISABLED
            self.fileName = ""
        else:
            self.files_.sort()
            self.folderPrevButton_["state"] = tk.NORMAL
            self.folderNextButton_["state"] = tk.NORMAL
            self.fileName = self.files_[0]

    # "Prev" button pressed
    #   => show previous grid
    def _prevFile(self):
        self.fileIndex_-=1
        if self.fileIndex_ < 0:
            self.fileIndex_ = len(self.files_) - 1

        # Update file name
        self.fileName = self.files_[self.fileIndex_]

    # "Next" button pressed
    #   => show next grid
    def _nextFile(self):
        self.fileIndex_+=1
        if self.fileIndex_ >= len(self.files_):
            self.fileIndex_ = 0

        # Update file name
        self.fileName = self.files_[self.fileIndex_]

    # File name
    @property
    def fileName(self):
        return self.fileNameEdit_.get()
    
    @fileName.setter
    def fileName(self, value):
        # change the file name
        if value is None:
            value = ""

        # Value changed ?
        if self.fileName == value : 
            # Nothing to do
            return
        
        self.fileEditButton_["state"] = tk.DISABLED if 0 == len(value) else tk.NORMAL
              
        self.fileNameEdit_.delete(0, tk.END)
        self.fileNameEdit_.insert(0, value)
        
        # File exists ?
        fullName = os.path.join(self.folderName, value)
        if os.path.exists(fullName):
            # Yes => draw the grid
            self.solver_.gridFromFile(fullName, False)

        # Solving is allowed ?
        state = tk.NORMAL if os.path.exists(fullName) else tk.DISABLED
        self.obviousValuesButton_["state"] = state
        self.solveButton_["state"] = state

    # Search and display obvious values
    #
    def _obviousValues(self):
        found, _ = self.solver_.findObviousValues()
        if found > 0:
            self.solver_.displayGrid()
    
    # Solve the selected grid
    #
    def _solve(self):
        if self.solver_ is not None:
            # Display mode
            self.solver_.setProgressMode(self.progressCombo_.current())           

            # solve ...
            res = self.solver_.resolve()

# 
#   Entry point
#
if '__main__' == __name__:
    try:
        # App using GUI
        main_window = sudoParamWindow()
        main_window.mainloop()
    except sudokuError as e:
        print(e)
        print(f"You should call {opts.APP_NAME}")
    except Exception as e:
        print(f"Unknown error - {str(e)}")   

# EOF