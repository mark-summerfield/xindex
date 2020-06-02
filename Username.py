#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import getpass
try:
    import win32api
except ImportError:
    win32api = None


def name():
    if win32api is not None:
        try:
            name = win32api.GetUserNameEx(win32api.NameDisplay)
            if name:
                return name
        except win32api.error:
            name = win32api.GetUserName()
            if name:
                return name
    try:
        name = getpass.getuser()
        if name:
            return name
    except Exception: # FIXME Make specific when it is documented
        pass
    return "User"
