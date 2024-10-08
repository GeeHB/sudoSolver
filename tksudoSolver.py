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
import tkoptions as tkopts
from options import options as opts

try:
    import tkinter as tk                    
    from tkinter import ttk
    import tkinter.font as tkFont
    import tkinter.messagebox as tkMB
    import tkinter.filedialog as tkDialog
except ModuleNotFoundError:
    print("tkinter module is not installed. Call ./sudoSolver.py instead")
    exit(1)

import os, sys
import sudoku
from sharedTools import systemInfos
import options as opts
from pygameOutputs import pygameOutputs

# Main window
# 
class sudoParamWindow(tk.Frame):

    # Construction
    def __init__(self, master = None):
    
        tk.Frame.__init__(self, master)
        self.grid()

        self.fileName_ = None
        self.config(width=tkopts.TK_WIN_WITH, height=tkopts.TK_WIN_HEIGHT)
    
        # members' values
        self.files_ = []

        # Change the default font ...
        self.ownFont_ = tkFont.nametofont("TkDefaultFont")
        self.ownFont_.configure(family="Arial", weight="normal", size=11)
        
        # Tab manager ...
        self.tabControl_ = ttk.Notebook(self) 

        # ... with 2 tabs
        self.gridsTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.gridsTab_, text = tkopts.TK_TAB_GRIDS)
        
        self.solveTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.solveTab_, text = tkopts.TK_TAB_SOLVE)

        self.tabControl_.pack(expand = 1, fill ="both")
        
        # "Grids" tab
        #

        # Folder name
        ttk.Label(self.gridsTab_, text = f"{tkopts.TK_FOLDERNAME} :").grid(column=0, row=0, padx=5, pady=5)
        
        self.folderNameEdit_ = ttk.Entry(self.gridsTab_)
        self.folderNameEdit_.grid(column=1, row=0, columnspan=3, padx=5, pady=5)

        self.folderBrowseButton_ = ttk.Button(self.gridsTab_, text=tkopts.TK_BROWSE, command=self._browseFolder)
        self.folderBrowseButton_.grid(column=4, row=0, padx=5, pady=5)

        # File name
        ttk.Label(self.gridsTab_, text = f"{tkopts.TK_FILENAME} :").grid(column=0, row=1, padx=5, pady=5)

        self.fileNameEdit_ = ttk.Entry(self.gridsTab_)
        self.fileNameEdit_.grid(column=1, row=1, columnspan=3, padx=5, pady=5)

        # "walk" buttons
        self.folderPrevButton_ = ttk.Button(self.gridsTab_, text=tkopts.TK_BROWSE_PREV, command = self._prevFile, state = tk.DISABLED)
        self.folderPrevButton_.grid(column=1, row=2, padx=5, pady=5)

        self.folderNextButton_ = ttk.Button(self.gridsTab_, text=tkopts.TK_BROWSE_NEXT, command = self._nextFile, state = tk.DISABLED)
        self.folderNextButton_.grid(column=2, row=2, padx=5, pady=5)

        # New grids (as a popup menu)
        self.newCombo_ = ttk.Menubutton(self.gridsTab_, text=tkopts.TK_NEW)
        self.newCombo_.menu = tk.Menu(self.newCombo_, tearoff=0)
        self.newCombo_["menu"] = self.newCombo_.menu

        # Choices in dropdown menu
        self.newCombo_.menu.add_cascade(label=tkopts.TK_NEW_EMPTY)
        self.newCombo_.menu.add_cascade(label=tkopts.TK_NEW_EASY)
        self.newCombo_.menu.add_cascade(label=tkopts.TK_NEW_MEDIUM)
        self.newCombo_.menu.add_cascade(label=tkopts.TK_NEW_HARD)
        self.newCombo_.grid(column=1, row=3, padx=5, pady=5, sticky="e")
        
        
        # File control buttons
        self.fileEditIcon_ = tk.PhotoImage(file="./assets/edit.png")
        self.fileEditButton_ = ttk.Button(self.gridsTab_, text=tkopts.TK_EDIT, 
                                    image = self.fileEditIcon_, compound=tk.LEFT,
                                    command=self._editGrid,
                                    state = tk.DISABLED)
        self.fileEditButton_.grid(column=2, row=3, padx=5, pady=25)

        # "Solve" tab
        #
        self.obviousValuesButton_ = ttk.Button(self.solveTab_, text=tkopts.TK_OBVIOUS_VALUES, command = self._obviousValues, state = tk.DISABLED)
        self.obviousValuesButton_.grid(column=0, row=0, columnspan=2, sticky = "w", padx=5, pady=5)

        ttk.Label(self.solveTab_, text = f"{tkopts.TK_SHOW_PROGRESS} :").grid(column=0, row=1, padx=5, pady=5)
        self.progressCombo_ = ttk.Combobox(self.solveTab_, state = "readonly")
        self.progressCombo_.grid(column=1, row=1, padx=5, pady=5)
        
        mySystem = systemInfos.getSystemInformations()
        
        if mySystem[systemInfos.KEY_OS] == systemInfos.OS_MACOS:
            # No multithread on MacOS
            self.progressCombo_["values"] = (tkopts.TK_PROGRESS_NONE, tkopts.TK_PROGRESS_SINGLETHREADED)
        else:
            self.progressCombo_["values"] = (tkopts.TK_PROGRESS_NONE, tkopts.TK_PROGRESS_SINGLETHREADED, tkopts.TK_PROGRESS_MULTITHREADED)
        self.progressCombo_.current(opts.options.PROGRESS_SLOW)  # show progress slowly by default 

        # Buttons
        self.solveIcon_ = tk.PhotoImage(file="./assets/solve.png")
        self.solveButton_ = ttk.Button(self.solveTab_, text=tkopts.TK_SOLVE,
                            image = self.solveIcon_, compound=tk.LEFT,
                            command = self._solve, state = tk.DISABLED)
        self.solveButton_.grid(column=0, row=3, sticky = "w", padx=5, pady=25)

        self.revertIcon_ = tk.PhotoImage(file="./assets/undo.png")
        self.revertButton_ = ttk.Button(self.solveTab_, text=tkopts.TK_REVERT,
                            image = self.revertIcon_, compound=tk.LEFT, 
                            command = self._revertGrid, state = tk.DISABLED)
        self.revertButton_.grid(column=1, row=3, padx=5, pady=25)
        
        self.saveIcon_ = tk.PhotoImage(file="./assets/save.png")
        self.saveButton_ = ttk.Button(self.solveTab_, text=tkopts.TK_SAVE, 
                            image = self.saveIcon_, compound=tk.LEFT, 
                            command = self._save, state = tk.DISABLED)
        self.saveButton_.grid(column=2, row=3, sticky = "w", padx=5, pady=25)

        # my sudoku solver
        self.solver_ = sudoku.sudoku(progressMode=opts.options.PROGRESS_SINGLETHREADED)

        # Default values
        self.backToSingltThreadMode_ = False
        self.fileName = ""
        self.folderName = os.path.abspath(opts.DEF_FOLDER)

    # Change folder
    #
    def _browseFolder(self):
        nFolder = tkDialog.askdirectory(title=tkopts.TK_CHOOSE_FOLDER, initialdir=self.folderName)
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

            tkMB.showwarning(tkopts.TK_GRID_FOLDER, f"No valid grid found in {self._shorter(value)}")
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

            if self.backToSingltThreadMode_:
                self.backToSingltThreadMode_ = False
                self.solver_.progressMode = opts.options.PROGRESS_SINGLETHREADED
                self.progressCombo_.current(self.solver_.progressMode)

            # Load the grid
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
            tkMB.showinfo(title=tkopts.TK_OBVIOUS_VALUES, message=f"Found {found} obvious value(s)")
        else:
            tkMB.showwarning(title=tkopts.TK_OBVIOUS_VALUES, message="No obvious value found")
    
    # Solve the selected grid
    #
    def _solve(self):
        if self.solver_ is not None:
            # Display mode
            self.solver_.progressMode = self.progressCombo_.current()
            
            # Display mode changed
            self.solver_.displayGrid()

            # Buttons state
            self.obviousValuesButton_["state"] = tk.DISABLED
            self.solveButton_["state"] = tk.DISABLED
            self.saveButton_["state"] = tk.DISABLED

            # solve ...
            res = self.solver_.resolve()
            self.solver_.displayGrid()

            # A solution ?
            if True == res[0]:
                tkMB.showinfo(title=tkopts.TK_SOLVING, message=f"Solved in {round(res[3], 2)} seconds")
                self.saveButton_["state"] = tk.NORMAL
            else:
                tkMB.showwarning(tkopts.TK_SOLVING, f"No solution found for grid in {self._shorter(self.fileName)}")

            # Return to "single threaded" 
            if self.solver_.progressMode == opts.options.PROGRESS_MULTITHREADED:
                self.backToSingltThreadMode_ = True

    # Create a new (empty) grid
    #
    def _createGrid(self):
        # Get name
        nFileName = tkDialog.asksaveasfilename(title=tkopts.TK_NEW_GRID, 
                            initialdir = self.folderName,
                            defaultextension=".txt",
                            filetypes=[("Text files", "*.txt")])
        if nFileName is not None and len(nFileName) > 0:
            # Changed folder ?
            res = os.path.split(nFileName)
            if res[0] != self.folderName:
                self.folderName = res[0]

            # (Create an) empty grid
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
                tkMB.showwarning(tkopts.TK_NEW_GRID, f"Unable to create {self._shorter(nFileName)}")

                # Draw the "old" grid
                fullName = os.path.join(self.folderName, self.fileName)
                self.solver_.gridFromFile(fullName, False)

    # Edit the selected gird
    #
    def _editGrid(self):
        tkMB.showinfo(title=tkopts.TK_GRID_EDITION, message="Press 'Enter' or 'Esc' to leave eidtion mode.")

        #self.solveTab_["state"] = tk.DISABLED
    
        done = self.solver_.edit()
        if done[0]:
            # Escaped => reload
            file = self.fileName
            self.fileName = file

        #self.solveTab_["state"] = tk.NORMAL

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
                tkMB.showinfo(tkopts.TK_SOLUTION, f"Soluce successfully saved in {name}")
            else:
                done = False
        except sudokuError as s:
            done = False

        if False == done:
            tkMB.showwarning(tkopts.TK_SOLUTION, f"Unable to save the soluce in {name}")

        self.saveButton_["state"] = tk.DISABLED

    # Get 'short' name
    #
    def _shorter(self, name):
        res = os.path.split(name)
        return res[1]
# 
#   Entry point
#
if "__main__" == __name__:
    try:
        # Window creation
        mainWindow = sudoParamWindow()
        mainWindow.master.title(tkopts.TK_TITLE)
        
        # App main loop
        quitLoop = False
        while not quitLoop:
            for event in mainWindow.solver_.getEvents():
                # Quit button on PYGame frame is pressed or tkFrame is already closed
                if event.type == pygameOutputs.EVT_QUIT or 0 == len(mainWindow.children) or mainWindow.master is None:
                    quitLoop = True
                    break
                
            if not quitLoop:
                mainWindow.solver_.flip()       # Update pygame
                mainWindow.master.update()      # handle GUI with tkinter

        # Should be useless be is necessary on ChromeOS !!!
        mainWindow.solver_.close()

    except sudokuError as e:
        print(f"Sudoku Error - {e}", file=sys.stderr)
    """
    except Exception as e:
        print(f"Unknown error - {str(e)}", file=sys.stderr)   
    """
# EOF