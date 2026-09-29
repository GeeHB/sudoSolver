# coding=UTF-8
#
#   File        :   menuConsts.py
#
#   Author      :   GeeHB
#
#   Description :
#

import wx  # pyright: ignore[reportMissingTypeStubs]

# File / New
#
IDM_FILE:str = '&File'
IDM_FILE_NEW:str = 'New'
ID_FILE_NEW_EMPTY:int = wx.NewIdRef()
IDM_FILE_NEW_EMPTY:str = 'Empty'
ID_FILE_NEW_EASY:int = wx.NewIdRef()
IDM_FILE_NEW_EASY:str = 'Easy'
ID_FILE_NEW_MEDIUM:int = wx.NewIdRef()
IDM_FILE_NEW_MEDIUM:str = 'Medium'
ID_FILE_NEW_HARD:int = wx.NewIdRef()
IDM_FILE_NEW_HARD:str = 'Hard'


# Edition
#
IDM_EDIT:str = '&Edit'
ID_EDIT_MODIFY:int =  wx.NewIdRef()
IDM_EDIT_MODIFY:str = 'Modify'



# Resolution
#
IDM_SOLVE:str = '&Solve'
ID_SOLVE_MANUAL:int =  wx.NewIdRef()
IDM_SOLVE_MANUAL:str = 'Manually'
ID_SOLVE_OBVIOUS:int =  wx.NewIdRef()
IDM_SOLVE_OBVIOUS:str = 'Obvious'

IDM_SOLVE_RESOLVE:str = 'Resolve'
ID_SOLVE_RESOLVE_SINGLE:int =  wx.NewIdRef()
IDM_SOLVE_RESOLVE_SINGLE:str= 'Single thread'
ID_SOLVE_RESOLVE_MULTI:int =  wx.NewIdRef()
IDM_SOLVE_RESOLVE_MULTI:str= 'Multi-threaded'

ID_SOLVE_REVERT:int =  wx.NewIdRef()
IDM_SOLVE_REVERT:str =  'Revert'



# EOF
