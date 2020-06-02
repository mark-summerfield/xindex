#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import Qt
from PySide.QtGui import (
    QApplication, QHBoxLayout, QIcon, QMainWindow, QPushButton,
    QTextBrowser, QVBoxLayout, QWidget)


class Form(QMainWindow):

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.setWindowTitle("{} — {}".format(
            title, QApplication.applicationName()))
        self.browser = QTextBrowser()
        self.browser.setOpenExternalLinks(False)
        self.browser.setOpenLinks(False)
        self.browser.setHtml(message)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Close")
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
        self.browser.setFocus()
        self.closeButton.clicked.connect(self.close)


if __name__ == "__main__":
    import sys
    import Qrc # noqa
    app = QApplication([])
    form = Form("Modeless Info", "<b>Bold data</b>")
    form.show()
    app.exec_()
