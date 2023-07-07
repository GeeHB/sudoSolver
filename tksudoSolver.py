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
    import tkinter.messagebox as tkMB
    import tkinter.filedialog as tkDialog
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
        ttk.Label(self.gridsTab_, text = "Folder name :").grid(column=0, row=0, padx=5, pady=5)
        
        self.folderNameEdit_ = ttk.Entry(self.gridsTab_)
        self.folderNameEdit_.grid(column=1, row=0, columnspan=3, padx=5, pady=5)

        self.folderBrowseButton_ = ttk.Button(self.gridsTab_, text="Browse", command=self._browseFolder)
        self.folderBrowseButton_.grid(column=5, row=0, padx=5, pady=5)

        # File name
        ttk.Label(self.gridsTab_, text = "File name :").grid(column=0, row=1, padx=5, pady=5)

        self.fileNameEdit_ = ttk.Entry(self.gridsTab_)
        self.fileNameEdit_.grid(column=1, row=1, columnspan=3, padx=5, pady=5)

        # "walk" buttons
        self.folderPrevButton_ = ttk.Button(self.gridsTab_, text="<<", command = self._prevFile, state = tk.DISABLED)
        self.folderPrevButton_.grid(column=1, row=2, padx=5, pady=5)

        self.folderNextButton_ = ttk.Button(self.gridsTab_, text=">>", command = self._nextFile, state = tk.DISABLED)
        self.folderNextButton_.grid(column=2, row=2, padx=5, pady=5)

        # File control buttons
        self.newIcon_ = tk.PhotoImage(file="./assets/new.png")
        self.fileCreateButton_ = ttk.Button(self.gridsTab_, text="Create",
                                    image = self.newIcon_, compound=tk.LEFT,
                                    command = self._createGrid)
        self.fileCreateButton_.grid(column=0, row=3, padx=5, pady=25)

        self.fileEditIcon_ = tk.PhotoImage(file="./assets/edit.png")
        self.fileEditButton_ = ttk.Button(self.gridsTab_, text="Edit", 
                                    image = self.fileEditIcon_, compound=tk.LEFT,
                                    command=self._editGrid,
                                    state = tk.DISABLED)
        self.fileEditButton_.grid(column=1, row=3, padx=5, pady=25)

        # "Solve" tab
        #
        self.obviousValuesButton_ = ttk.Button(self.solveTab_, text="Obvious values", command = self._obviousValues, state = tk.DISABLED)
        self.obviousValuesButton_.grid(column=0, row=0, columnspan=2, sticky = "w", padx=5, pady=5)

        ttk.Label(self.solveTab_, text = "Show progress :").grid(column=0, row=1, padx=5, pady=5)
        self.progressCombo_ = ttk.Combobox(self.solveTab_, state = "readonly")
        self.progressCombo_.grid(column=1, row=1, padx=5, pady=5)
        self.progressCombo_["values"] = ("none", "slow", "multithreaded")
        self.progressCombo_.current(opts.options.PROGRESS_SINGLETHREADED)  # show progress slowly 

        # Buttons
        self.solveIcon_ = tk.PhotoImage(file="./assets/solve.png")
        self.solveButton_ = ttk.Button(self.solveTab_, text="Solve",
                            image = self.solveIcon_, compound=tk.LEFT,
                            command = self._solve, state = tk.DISABLED)
        self.solveButton_.grid(column=0, row=3, sticky = "w", padx=5, pady=25)

        self.revertIcon_ = tk.PhotoImage(file="./assets/undo.png")
        self.revertButton_ = ttk.Button(self.solveTab_, text="Revert",
                            image = self.revertIcon_, compound=tk.LEFT, 
                            command = self._revertGrid, state = tk.DISABLED)
        self.revertButton_.grid(column=1, row=3, padx=5, pady=25)
        
        self.saveIcon_ = tk.PhotoImage(file="./assets/save.png")
        self.saveButton_ = ttk.Button(self.solveTab_, text="Save", 
                            image = self.saveIcon_, compound=tk.LEFT, 
                            command = self._save, state = tk.DISABLED)
        self.saveButton_.grid(column=2, row=3, sticky = "w", padx=5, pady=25)

        # Default values
        self.fileName = ""
        self.folderName = os.path.abspath(opts.DEF_FOLDER)

    # Change folder
    #
    def _browseFolder(self):
        nFolder = tkDialog.askdirectory(title="Choose grids'folder", initialdir=self.folderName)
        if nFolder is not None and len(nFolder) > 0 and nFolder != self.folderName:
            # User choose a new folder
            self.folderName = nFolder
    
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

            tkMB.showwarning("Grid folder", f"No grid found in {value}")
        else:
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
        # Change the file name
        if value is None:
            value = ""

        # Value changed ?
        if self.fileName == value : 
            # Nothing to do
            return
        
        state = tk.DISABLED if 0 == len(value) else tk.NORMAL
        self.fileEditButton_["state"] = state
        self.revertButton_["state"] = state
              
        self.fileNameEdit_.delete(0, tk.END)
        self.fileNameEdit_.insert(0, value)
        
        # File exists ?
        self.validGrid_ = False
        fullName = os.path.join(self.folderName, value)
        if os.path.exists(fullName):
            # Yes => draw the grid
            if False == self.solver_.gridFromFile(fullName, False):
                # the file doesn't contain a valid grid
                self.solver_.displayGrid()
            else:
                self.validGrid_ = True

        # Solving is allowed ?
        state = tk.NORMAL if self.validGrid_ else tk.DISABLED
        self.obviousValuesButton_["state"] = state
        self.solveButton_["state"] = state
        self.fileEditButton_["state"] = state

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

            # Buttons state
            self.obviousValuesButton_["state"] = tk.DISABLED
            self.solveButton_["state"] = tk.DISABLED
            self.saveButton_["state"] = tk.DISABLED

            # solve ...
            res = self.solver_.resolve()

            # A solution ?
            if True == res[0]:
                self.saveButton_["state"] = tk.NORMAL

    # Create a new (empty) grid
    #
    def _createGrid(self):
        # Get name
        nFileName = tkDialog.asksaveasfilename(title="New grid", 
                            initialdir = self.folderName,
                            defaultextension=".txt",
                            filetypes=[("Text files", "*.txt")])
        if nFileName is not None and len(nFileName) > 0:
            # Changed folder ?
            res = os.path.split(nFileName)
            if res[0] != self.folderName:
                self.folderName = res[0]

            # Create an empty grid
            self.solver_.emptyGrid()

            # Save it
            self.solver_.save(newFileName=nFileName)

            # update the file list
            self.solver_.folderContent(res[0], self.files_)

            # new file index (and new file name)
            try:
                self.fileIndex_ = self.files_.index(res[1])
                
                # Change the filename in the main window
                self.fileName = res[1]
            except IndexError:
                # The file is not found in the list
                tkMB.showwarning("New grid", f"Unable to create {nFileName}")

                # Draw the "old" grid
                fullName = os.path.join(self.folderName, self.fileName)
                self.solver_.gridFromFile(fullName, False)

    # Edit the selected gird
    #
    def _editGrid(self):
        tkMB.showinfo(title="Grid edition", message="Press 'Enter' when edition is finished.")

        self.solveTab_["state"] = tk.DISABLED
        self.solver_.edit()
        self.solveTab_["state"] = tk.NORMAL

    # Revert (ie. return the grid to the previous saved state)
    #
    def _revertGrid(self):
        self.solver_.revertGrid()
        self.solver_.displayGrid()

        # Buttons'state
        self.solveButton_["state"] = tk.NORMAL
        self.obviousValuesButton_["state"] = tk.NORMAL

    # Save the solution
    #
    def _save(self):
        done = True
        try:
            name = self.solver_.save(True)
            if name is not None:
                tkMB.showinfo("Solution", f"Soluce successfully saved in {name}")
            else:
                done = False
        except sudokuError as s:
            done = False

        if False == done:
            tkMB.showwarning("Solution", f"Unable to save the soluce in {name}")

        self.saveButton_["state"] = tk.DISABLED
# 
#   Entry point
#
if "__main__" == __name__:
    try:
        # App using GUI
        mainWindow = sudoParamWindow()
        mainWindow.mainloop()
    except sudokuError as e:
        print(e)
    except Exception as e:
        print(f"Unknown error - {str(e)}")   

# EOF