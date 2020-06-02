#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import logging
import multiprocessing
import os
import sys
import tempfile

import PySide
from PySide.QtCore import (
    qVersion, QSettings, qInstallMsgHandler, QtCriticalMsg, QtDebugMsg,
    QtFatalMsg, QtWarningMsg)
from PySide.QtGui import QApplication, QIcon, QPixmap, QSplashScreen
import PySide.QtSvg # for icons
import PySide.QtXml # for icons

import Const


application = QApplication(sys.argv) # Needed as early as possible


APPNAME = "XindeX"
__version__ = "1.5.0"

DEBUGGING = len(sys.argv) > 1 and sys.argv[1] in {"--debug", "-D"}
if DEBUGGING:
    sys.argv.pop(1)
    import apsw
    import traceback
    # sys.setrecursionlimit(50)
else:
    sys.tracebacklimit = 0 # Minimize tracebacks for end user
    sys.excepthook = lambda *args: None # No tracebacks

LOGFILE = os.path.join(tempfile.gettempdir(), "XindeX.log")
logging.basicConfig(filename=LOGFILE, filemode="w", level=logging.DEBUG,
                    format="%(levelname)s: %(message)s")


def error(message):
    logging.warn(message)
    window = QApplication.activeWindow() # Doesn't matter if it is None
    form = MessageForm.Form("Error", str(message), window)
    form.show() # Modeless; returns immediately


Const.error = error


def say(message, timeout=0):
    if say.statusbar is None:
        for window in QApplication.topLevelWidgets():
            if hasattr(window, "statusbar"):
                say.statusbar = getattr(window, "statusbar")
                break
    if say.statusbar is not None:
        say.statusbar.showMessage(message, timeout)
    else:
        error(message)


say.statusbar = None
Const.say = say


# These *must* come after the Const module has been set up
import Lib
import MessageForm
import Window
from Config import Gopt


def main():
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        raise SystemExit("usage: {} file{}".format(
                         os.path.basename(sys.argv[0]), Const.SUFFIX))
    _setupApplication()
    splash = _maybeSplash()
    if DEBUGGING:
        _showVersions()
    try:
        application.processEvents()
        window = Window.Window(DEBUGGING)
        if splash is not None:
            splash.finish(window)
        application.exec_()
        if (sys.stdout is not None and os.isatty(sys.stdout.fileno()) and
                os.path.getsize(LOGFILE)):
            with open(LOGFILE, "rt", encoding="utf-8") as file:
                print(ascii(file.read()) if Const.WIN else file.read(),
                      end="")
    except Exception as err:
        if DEBUGGING:
            traceback.print_last()
        print("unexpected error: {}".format(err))


def _setupApplication():
    application.setOrganizationName("Qtrac Ltd.")
    application.setOrganizationDomain("qtrac.eu")
    application.setApplicationName(APPNAME)
    application.setApplicationVersion(__version__)
    application.addLibraryPath(Lib.get_path("imageformats"))
    # Needed for 64-bit builds; harmless for 32-bit
    for plugin_path in (os.path.join(path, "plugins")
                        for path in PySide.__path__):
        application.addLibraryPath(plugin_path)
    application.setWindowIcon(QIcon(":/xindex.svg"))


def _maybeSplash():
    splash = None
    settings = QSettings()
    if bool(int(settings.value(Gopt.Key.ShowSplash,
                               Gopt.Default.ShowSplash))):
        splash = QSplashScreen(QPixmap(":/splash.png"))
        splash.show()
        application.processEvents()
    return splash


def _showVersions():
    print("XindeX {} - Python {}.{}.{}/{} - Qt {} - PySide {} - APSW {} "
          "- SQLite {}".format(
              QApplication.applicationVersion(), sys.version_info.major,
              sys.version_info.minor, sys.version_info.micro,
              "64" if Const.IS64BIT else 32, qVersion(),
              PySide.__version__, apsw.apswversion(),
              apsw.sqlitelibversion()))


def _messageHandler(kind, message):
    logger = {QtCriticalMsg: logging.critical, QtDebugMsg: logging.debug,
              QtFatalMsg: logging.error, QtWarningMsg: logging.warning
              }[kind]
    pair = (kind, message)
    if pair not in _messageHandler.seen:
        _messageHandler.seen.add(pair)
        logger(message)


_messageHandler.seen = set()

qInstallMsgHandler(_messageHandler)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
