#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import datetime
import platform
import sys

import apsw
import PySide
from PySide.QtCore import qVersion
from PySide.QtGui import QApplication, QKeySequence, QMessageBox

import Lib
from Const import IS64BIT


class Actions:

    def __init__(self, window):
        self.window = window
        self.state = self.window.state
        # self.viewWindow = None
        self.helpAction = Lib.createAction(
            window, ":/help.svg", "&Help", self.state.help,
            QKeySequence.HelpContents, """\
<p><b>Help→Help</b> ({})</p>
<p>Show the online help.</p>""".format(
                QKeySequence(QKeySequence.HelpContents).toString()))
        self.aboutAction = Lib.createAction(
            window, ":/xindex.svg", "&About", self.about,
            tooltip="""\
<p><b>Help→About</b></p>
<p>Show {}'s About box.</p>""".format(QApplication.applicationName()))


    def forMenu(self):
        return (self.helpAction, self.aboutAction)


    def forToolbar():
        return ()


    def about(self):
        widget = QApplication.focusWidget()
        year = datetime.date.today().year
        year = "2015-{}".format(str(year)[-2:]) if year != 2015 else "2015"
        w = self.window.frameGeometry().width()
        h = self.window.frameGeometry().height()
        with Lib.Qt.DisableUI(*self.window.widgets(), forModalDialog=True):
            app = QApplication.applicationName()
            version = QApplication.applicationVersion()
            bits = 64 if IS64BIT else 32
            QMessageBox.about(
                self.window, "About — {}".format(
                    QApplication.applicationName()), f"""
<p><b><font color=navy>{app} {version}</font></b></p>
<p><font color=navy>{app} is an easy to learn and use application
for creating, editing, and outputting indexes (e.g., for
books).</font>
</p>
<p>Copyright © Qtrac Ltd {year}. All Rights Reserved.</p>
<p>License:&nbsp;GPLv3.</p>
<hr>
<p>Window size: {w:,}x{h:,}</p>
<p>
Python
{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}/{
bits}-bit<br>
PySide {PySide.__version__}<br>
Qt {qVersion()}<br>
APSW {apsw.apswversion()}<br>
SQLite {apsw.sqlitelibversion()}<br>
{platform.platform()}</p>""")
        Lib.restoreFocus(widget)
