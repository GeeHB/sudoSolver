#!/usr/bin/python3
#
# coding=UTF-8
#
#   File        :   tkSudoku.py
#
#   Author      :   GeeHB
#
#   Description :   App's GUI using tkinter
#

import tkinter as tk                    
from tkinter import ttk
import os

import options as opts

# Main window handling app's parameters
# 
class paramWindow(tk.Tk):

    # Construction
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fileName_ = None
        self.config(width=opts.APP_GUI_WITH, height=opts.APP_GUI_HEIGHT)
        self.title(opts.APP_GUI_TITLE)

        # members' values
        self.files_ = []

        # Tab manager ...
        self.tabControl_ = ttk.Notebook(self) 

        # ... with 3 tabs
        self.foldersTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.foldersTab_, text = opts.APP_GUI_TAB_FOLDERS)
        
        self.fileTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.fileTab_, text = opts.APP_GUI_TAB_FILES)

        self.solveTab_ = ttk.Frame(self.tabControl_)
        self.tabControl_.add(self.solveTab_, text = opts.APP_GUI_TAB_SOLVE)

        self.tabControl_.pack(expand = 1, fill ="both")

        # "Folders" tab
        ttk.Label(self.foldersTab_, text = 'Folder name :').grid(column=0, row=0, padx=15, pady=15)
        
        self.folderNameEdit_ = ttk.Entry(self.foldersTab_)
        self.folderNameEdit_.grid(column=1, row=0, columnspan=3, padx=5, pady=15)
        
        self.folderBrowseButton_ = ttk.Button(self.foldersTab_, text='Browse')
        self.folderBrowseButton_.grid(column=5, row=0, padx=5, pady=15)

        self.folderPrevButton_ = ttk.Button(self.foldersTab_, text='<<', command = self._prevFile, state = tk.DISABLED)
        self.folderPrevButton_.grid(column=1, row=1, padx=5, pady=15)

        self.folderNextButton_ = ttk.Button(self.foldersTab_, text='>>', command = self._nextFile, state = tk.DISABLED)
        self.folderNextButton_.grid(column=3, row=1, padx=5, pady=15)

        # "File" tab
        ttk.Label(self.fileTab_, text = 'File name :').grid(column=0, row=0, padx=15, pady=15)
        
        self.fileNameEdit_ = ttk.Entry(self.fileTab_)
        self.fileNameEdit_.grid(column=1, row=0, columnspan=3, padx=5, pady=15)
        
        self.fileCreateButton_ = ttk.Button(self.fileTab_, text='Create')
        self.fileCreateButton_.grid(column=5, row=0, padx=5, pady=15)

        self.fileEditButton_ = ttk.Button(self.fileTab_, text='Edit', state = tk.DISABLED)
        self.fileEditButton_.grid(column=3, row=1, padx=5, pady=15)

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

        self.files_.clear()
        self.fileIndex_ = 0

        # Folder content
        if len(val) > 0:
            # Only this folder
            for (_, _, fileNames) in os.walk(val):
                self.files_.extend(fileNames)
                break

        # No solution files in the list !
        for file in self.files_ :
            _, fileExt = os.path.splitext(file)
            if opts.FILE_EXPORT_EXTENSION == fileExt:
                # remove the file from the list
                self.files_.remove(file)  

        if len(self.files_) == 0:
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
    def _prevFile(self):
        self.fileIndex_-=1
        if self.fileIndex_ < 0:
            self.fileIndex_ = len(self.files_) - 1

        # Update file name
        self.fileName = self.files_[self.fileIndex_]

    # "Next" button pressed
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
            pass

# 
#   Entry point
#
if '__main__' == __name__:

  main_window = paramWindow()
  main_window.mainloop()

# EOF