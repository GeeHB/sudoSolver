# coding=UTF-8
#
#   File        :   menuConsts.py
#
#   Author      :   GeeHB
#
#   Description :
#

import wx  # pyright: ignore[reportMissingTypeStubs]

# Files
#
IDM_FILE:str = '&File'
IDM_THEMES:str = 'Themes'

# Creation
#
IDM_CREATE:str = '&Create'
ID_CREATE_EMPTY:int = wx.NewIdRef().GetId()
IDM_CREATE_EMPTY:str = 'Empty\tCtrl+0'
ID_CREATE_EASY:int = wx.NewIdRef().GetId()
IDM_CREATE_EASY:str = 'Easy\tCtrl+1'
ID_CREATE_MEDIUM:int = wx.NewIdRef().GetId()
IDM_CREATE_MEDIUM:str = 'Medium\tCtrl+2'
ID_CREATE_HARD:int = wx.NewIdRef().GetId()
IDM_CREATE_HARD:str = 'Hard\tCtrl+3'

ID_EDIT_UNDO:int =  wx.NewIdRef().GetId()
IDM_CREATE_UNDO:str = 'Undo\tCtrl+Z'
ID_EDIT_MODIFY:int =  wx.NewIdRef().GetId()
IDM_CREATE_MODIFY:str = '&Modify\tCtrl+M'
ID_EDIT_DONE:int =  wx.NewIdRef().GetId()
IDM_CREATE_DONE:str = 'Done\tEnter'
ID_EDIT_CANCEL:int =  wx.NewIdRef().GetId()
IDM_CREATE_CANCEL:str = 'Cancel\tEsc'


# Resolution
#
IDM_SOLVE:str = '&Solve'
ID_SOLVE_MANUAL:int =  wx.NewIdRef().GetId()
IDM_SOLVE_MANUAL:str = 'Manually'
ID_SOLVE_OBVIOUS:int =  wx.NewIdRef().GetId()
IDM_SOLVE_OBVIOUS:str = 'Obvious'

IDM_SOLVE_RESOLVE:str = 'Resolve'
ID_SOLVE_RESOLVE_SINGLE:int =  wx.NewIdRef().GetId()
IDM_SOLVE_RESOLVE_SINGLE:str= 'Single thread'
ID_SOLVE_RESOLVE_MULTI:int =  wx.NewIdRef().GetId()
IDM_SOLVE_RESOLVE_MULTI:str= 'Multi-threaded'

ID_SOLVE_REVERT:int =  wx.NewIdRef().GetId()
IDM_SOLVE_REVERT:str =  'Revert\tCtrl+R'

# Contextual menu
#
IDM_POPUP_EMPTY:str = "Empty"
ID_POPUP_VALUES:list[int] =  [wx.NewIdRef().GetId() for _ in range(10)]



# EOF
