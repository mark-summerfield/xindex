#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

try:
    import winreg
except ImportError:
    winreg = None
import logging
import os

from PySide.QtCore import QSettings
from PySide.QtGui import QApplication

from .Lib import get_path


FILE_TYPE_NAME = "xindex.xix"


def maybe_register_filetype(debug=False):
    if winreg is None: # Windows only
        return
    settings = QSettings()
    if bool(int(settings.value("Registered", 0))):
        return # Already registered

    exe = get_path("xindex.exe")
    if not os.path.exists(exe):
        if debug:
            print("no executable '{}'".format(exe))
        return
    icon = exe + ",1"
    extensionCommand = '"{}" "%L" %*'.format(exe)
    who = winreg.HKEY_CURRENT_USER
    access = winreg.KEY_ALL_ACCESS
    root = r"Software\Classes"
    base = root + r"\{}".format(FILE_TYPE_NAME)
    ok = True

    items = ((root + r"\.xix", FILE_TYPE_NAME),
             (base, "{} file".format(QApplication.applicationName())),
             (base + r"\DefaultIcon", icon),
             (base + r"\shell", ""),
             (base + r"\shell\open", ""),
             (base + r"\shell\open\command", extensionCommand),
             )

    for i, (name, value) in enumerate(items, 1):
        try:
            key = winreg.CreateKeyEx(who, name, access=access)
            winreg.SetValue(key, "", winreg.REG_SZ, value)
            winreg.CloseKey(key)
        except OSError as err:
            ok = False
            print("failed to set file association #{}: {}".format(i, err))
            logging.warning("failed to set file association #{}: {}"
                            .format(i, err))
    if ok:
        settings.setValue("Registered", 1)
