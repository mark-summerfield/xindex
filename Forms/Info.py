#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import html
import re
import os
import time

from PySide.QtCore import QDateTime, QDir, QFileInfo, QLocale, QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QHBoxLayout, QIcon, QPushButton,
    QTextBrowser, QVBoxLayout)

import Lib
from Config import Gconf, Gopt
from Const import UUID


@Lib.updatable_tooltips
class Form(QDialog):


    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModal)
        self.setWindowFlags(
            self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.initialize()
        if parent is not None:
            self.resize(max(400, parent.width() // 2),
                        max(400, parent.height() // 3))
        self.setWindowTitle("Information — {}".format(
                            QApplication.applicationName()))
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.browser = QTextBrowser()
        self.tooltips.append((self.browser, """<p><b>Information</b></p>
<p>Show basic information about the current index.</p>"""))
        self.browser.zoomIn(1)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
        self.tooltips.append((self.closeButton, """<p><b>Close</b></p>
<p>Close the dialog.</p>"""))
        self.closeButton.clicked.connect(self.reject)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.browser, 1)
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.closeButton)
        hbox.addStretch()
        layout.addLayout(hbox)
        self.setLayout(layout)


    def initialize(self):
        locale = QLocale()
        model = self.state.model
        if not bool(model):
            self.browser.setHtml("<font color=red>Information can only "
                                 "be shown if an index is open</font>")
            return

        top, total, _ = self.state.indicatorCounts()
        fullname = QDir.toNativeSeparators(os.path.abspath(model.filename))
        creator = model.config(Gconf.Key.Creator)
        created = model.config("Created")
        created = locale.toString(QDateTime.fromString(created,
                                  "yyyy-MM-dd HH:mm:ss"))
        updated = locale.toString(QFileInfo(model.filename).lastModified())
        size = os.path.getsize(model.filename)
        KB = 1024
        MB = KB * KB
        if size < MB:
            size = "~{:,} KB ({:,} bytes)".format(round(size / KB), size)
        else:
            size = "~{:,} MB ({:,} bytes)".format(round(size / MB), size)
        filename = re.sub(r"\.xix$", "", os.path.basename(fullname),
                          re.IGNORECASE)
        version = str(model.version())
        secs = self.state.workTime + int(time.monotonic() -
                                         self.state.startTime)
        hours, secs = divmod(secs, 3600)
        if hours:
            worktime = "{:,}h{}'".format(hours, secs // 60)
        else:
            worktime = "{}'".format(secs // 60)
        uuid = model.config(UUID)
        LEFT_STYLE = """ style="
margin-right: 0;
padding-right: 0;
spacing-right: 0;
border-right: 0;
"
"""
        RIGHT_STYLE = """ style="
margin-left: 0;
padding-left: 0;
spacing-left: 0;
border-left: 0;
"
"""
        color1 = "#DDDDFF"
        color2 = "#EEEEFF"
        STYLE = ' style="background-color: {};"'
        texts = ["""<html><table border=0 style="
background-color: {};
">""".format(color1)]
        for i, (name, value, right, debug) in enumerate((
            ("Index", filename, False, False),
            ("Creator", creator, False, False),
            ("Filename", fullname, False, False),
            ("Size", size, False, False),
            ("Created", created, False, False),
            ("Updated", updated, False, False),
            ("Total Entries", "{:,}".format(total), True, False),
            ("Main Entries", "{:,}".format(top), True, False),
            ("Subentries", "{:,}".format(total - top), True, False),
            ("Worktime", worktime, True, False),
            (None, None, False, False),
            ("Index Format", version, True, False),
            ("Index UUID", uuid, True, True),
                )):
            if debug and not self.state.window.debug:
                continue
            if name is None:
                color1 = "#EEEEEE"
                color2 = "#DDDDDD"
                continue
            style = STYLE.format(color1 if i % 2 == 0 else color2)
            align = " align=right" if right else ""
            texts.append("""<tr{}><td{}>{}&nbsp;&nbsp;</td>
<td{}{}>{}</td></tr>""".format(
                style, LEFT_STYLE, html.escape(name), align, RIGHT_STYLE,
                html.escape(value)))
        texts.append("</table></html>")
        self.browser.setHtml("".join(texts))
