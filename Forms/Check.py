#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, QSize, Qt, Signal
from PySide.QtGui import (
    QApplication, QHBoxLayout, QIcon, QMainWindow, QPushButton,
    QTextBrowser, QVBoxLayout, QWidget)

import Lib
from Config import Gopt
from Const import MAIN_INDICATOR, ROOT, SUB_INDICATOR


class Form(QMainWindow):

    requestGotoEid = Signal(str, int) # uuid, eid


    def __init__(self, state, eids, uuid, name, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("Check “{}” — {}".format(
                            name, QApplication.applicationName()))
        self.state = state
        self.uuid = uuid
        self.loadSaveSize = False
        self.createWidgets(eids, name)
        self.layoutWidgets()
        self.createConnections()
        self.browser.setFocus()


    def createWidgets(self, eids, name):
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setOpenLinks(False)
        text = ["<html>"]
        if not eids:
            text.append("<font color=darkgreen>No entries match the "
                        "“{}” check.</font>".format(name))
        else:
            self.loadSaveSize = True
            text.append("<p><font color=navy>{:,} entries match the "
                        "“{}” check.</font></p>".format(len(eids), name))
            for eid in eids:
                entry = self.state.model.entry(eid)
                if entry:
                    term = Lib.elidePatchHtml(entry.term, self.state)
                    prefix = "{} ".format(
                        MAIN_INDICATOR if entry.peid == ROOT else
                        SUB_INDICATOR)
                    text.append('{}<a href="{}">{}</a><br>'.format(
                                prefix, eid, term))
        text.append("</html>")
        self.browser.setHtml("".join(text))
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")


    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(self.closeButton)
        hbox.addStretch()
        layout.addWidget(self.browser)
        layout.addLayout(hbox)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        if self.loadSaveSize:
            settings = QSettings()
            self.resize(QSize(settings.value(Gopt.Key.CheckForm_Size,
                                             Gopt.Default.CheckForm_Size)))


    def createConnections(self):
        self.browser.anchorClicked.connect(self.gotoEid)
        self.closeButton.clicked.connect(self.close)


    def closeEvent(self, event=None):
        if self.loadSaveSize:
            settings = QSettings()
            settings.setValue(Gopt.Key.CheckForm_Size, self.size())
        super().closeEvent(event)


    def gotoEid(self, link):
        self.requestGotoEid.emit(self.uuid, int(link.toString()))


if __name__ == "__main__":
    import sys
    import Qrc # noqa
    app = QApplication([])
    class State:
        pass
    form = Form(State(), [], "UUID", "A check")
    form.show()
    app.exec_()
