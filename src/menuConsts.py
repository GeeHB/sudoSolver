# coding=UTF-8
#
#   File        :   menuConsts.py
#
#   Author      :   GeeHB
#
#   Description :
#

import wx  # pyright: ignore[reportMissingTypeStubs]

import appStrings

# Files
#
IDS_FILE:str = '&File'

# Display
#
IDS_DISPLAY:str = f"&{appStrings.STR_DISPLAY_MENU}"

IDS_DISPLAY_CENTER:str = appStrings.STR_DISPLAY_CENTER
ID_DISPLAY_CENTER:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

IDS_DISPLAY_HELP:str = appStrings.STR_DISPLAY_HELP
ID_DISPLAY_HELP:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]

IDS_DISPLAY_THEMES:str = appStrings.STR_DISPLAY_THEMES

# Creation
#
IDS_CREATE:str = f"&{appStrings.STR_CREATE_MENU}"
ID_CREATE_EMPTY:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_EMPTY:str = f"{appStrings.STR_CREATE_EMPTY}\tCtrl+0"
ID_CREATE_EASY:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_EASY:str = f"{appStrings.STR_CREATE_EASY}\tCtrl+1"
ID_CREATE_MEDIUM:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_MEDIUM:str = f"{appStrings.STR_CREATE_MEDIUM}\tCtrl+2"
ID_CREATE_HARD:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_HARD:str = f"{appStrings.STR_CREATE_HARD}\tCtrl+3"

ID_EDIT_UNDO:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_UNDO:str = f"{appStrings.STR_CREATE_UNDO}\tCtrl+Z"
ID_EDIT_MODIFY:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_MODIFY:str = f"&{appStrings.STR_CREATE_MODIFY}\tCtrl+M"
ID_EDIT_DONE:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_CREATE_DONE:str = f"{appStrings.STR_CREATE_DONE}\tEnter"
ID_EDIT_CANCEL:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportRedeclaration, reportUnknownVariableType]
IDS_CREATE_CANCEL:str = f"{appStrings.STR_CREATE_CANCEL}\tEsc"

# Resolution
#
ID_SOLVE:int = wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE:str = f"&{appStrings.STR_SOLVE_MENU}"
ID_SOLVE_MANUAL:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE_MANUAL:str = appStrings.STR_SOLVE_MANUAL
ID_SOLVE_OBVIOUS:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE_OBVIOUS:str = appStrings.STR_SOLVE_OBVIOUS

IDS_SOLVE_RESOLVE:str = appStrings.STR_SOLVE_RESOLVE
ID_SOLVE_RESOLVE_SINGLE:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE_RESOLVE_SINGLE:str= appStrings.STR_SOLVE_RESOLVE_SINGLE
ID_SOLVE_RESOLVE_MULTI:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE_RESOLVE_MULTI:str= appStrings.STR_SOLVE_RESOLVE_MULTI

ID_SOLVE_REVERT:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_SOLVE_REVERT:str =  f"{appStrings.STR_SOLVE_REVERT}\tCtrl+R"

# Hypothesis and tags
#
IDS_TIP_HYP_COMBO:str = "List of colored hyptothesis"

ID_HYP_VALIDATE:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_HYP_VALIDATE:str =  appStrings.STR_HYP_VALIDATE
IDS_TIP_HYP_VALIDATE:str = appStrings.STR_TIP_HYP_VALIDATE

ID_HYP_REJECT:int =  wx.NewIdRef().GetId()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_HYP_REJECT:str =  appStrings.STR_HYP_REJECT
IDS_TIP_HYP_REJECT:str = appStrings.STR_TIP_HYP_REJECT

ID_EDIT_END:int =  ID_EDIT_DONE  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
IDS_EDIT_END:str =  appStrings.STR_EDIT_END
IDS_TIP_EDIT_END:str = appStrings.STR_TIP_EDIT_END

ID_EDIT_CANCEL:int =  ID_EDIT_CANCEL  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType, reportConstantRedefinition]  # noqa: PLW0127
IDS_EDIT_CANCEL:str =  appStrings.STR_EDIT_CANCEL
IDS_TIP_EDIT_CANCEL:str = appStrings.STR_TIP_EDIT_CANCEL

# Contextual menu
#
IDS_POPUP_EMPTY:str = appStrings.STR_POPUP_EMPTY
ID_POPUP_VALUES:list[int] =  [wx.NewIdRef().GetId() for _ in range(10)]  # pyright: ignore[reportUnknownMemberType]

# EOF
