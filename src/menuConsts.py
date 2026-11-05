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
IDS_FILE:str = '&File'

# Display
#
IDS_DISPLAY:str = '&Display'

IDS_DISPLAY_CENTER:str = 'Center array'
ID_DISPLAY_CENTER:int = wx.NewIdRef().GetId()

IDS_DISPLAY_HELP:str = 'Show help matrix'
ID_DISPLAY_HELP:int = wx.NewIdRef().GetId()

IDS_DISPLAY_THEMES:str = 'Themes'


# Creation
#
IDS_CREATE:str = '&Create'
ID_CREATE_EMPTY:int = wx.NewIdRef().GetId()
IDS_CREATE_EMPTY:str = 'Empty\tCtrl+0'
ID_CREATE_EASY:int = wx.NewIdRef().GetId()
IDS_CREATE_EASY:str = 'Easy\tCtrl+1'
ID_CREATE_MEDIUM:int = wx.NewIdRef().GetId()
IDS_CREATE_MEDIUM:str = 'Medium\tCtrl+2'
ID_CREATE_HARD:int = wx.NewIdRef().GetId()
IDS_CREATE_HARD:str = 'Hard\tCtrl+3'

ID_EDIT_UNDO:int =  wx.NewIdRef().GetId()
IDS_CREATE_UNDO:str = 'Undo\tCtrl+Z'
ID_EDIT_MODIFY:int =  wx.NewIdRef().GetId()
IDS_CREATE_MODIFY:str = '&Modify\tCtrl+M'
ID_EDIT_DONE:int =  wx.NewIdRef().GetId()
IDS_CREATE_DONE:str = 'Done\tEnter'
ID_EDIT_CANCEL:int =  wx.NewIdRef().GetId()
IDS_CREATE_CANCEL:str = 'Cancel\tEsc'


# Resolution
#
ID_SOLVE:int = wx.NewIdRef().GetId()
IDS_SOLVE:str = '&Solve'
ID_SOLVE_MANUAL:int =  wx.NewIdRef().GetId()
IDS_SOLVE_MANUAL:str = 'Manually'
ID_SOLVE_OBVIOUS:int =  wx.NewIdRef().GetId()
IDS_SOLVE_OBVIOUS:str = 'Obvious'

IDS_SOLVE_RESOLVE:str = 'Resolve'
ID_SOLVE_RESOLVE_SINGLE:int =  wx.NewIdRef().GetId()
IDS_SOLVE_RESOLVE_SINGLE:str= 'Single thread'
ID_SOLVE_RESOLVE_MULTI:int =  wx.NewIdRef().GetId()
IDS_SOLVE_RESOLVE_MULTI:str= 'Multi-threaded'

ID_SOLVE_REVERT:int =  wx.NewIdRef().GetId()
IDS_SOLVE_REVERT:str =  'Revert\tCtrl+R'

ID_HYP_VALIDATE:int =  wx.NewIdRef().GetId()
IDS_HYP_VALIDATE:str =  'Validate'
IDS_TIP_HYP_VALIDATE:str = 'Validate current colored hyptothesis'

ID_HYP_REJECT:int =  wx.NewIdRef().GetId()
IDS_HYP_REJECT:str =  'Reject'
IDS_TIP_HYP_REJECT:str = 'Reject the current hyptothesis'

ID_EDIT_END:int =  ID_EDIT_DONE
IDS_EDIT_END:str =  'End'
IDS_TIP_EDIT_END:str = 'Stop edition'

# Contextual menu
#
IDS_POPUP_EMPTY:str = "Empty"
ID_POPUP_VALUES:list[int] =  [wx.NewIdRef().GetId() for _ in range(10)]



# EOF
