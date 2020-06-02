#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QDialog, QDialogButtonBox, QTextBrowser, QVBoxLayout)


class Form(QDialog):

    def __init__(self, title, message, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setWindowTitle("{} — XindeX".format(title))
        self.create_widgets(message)
        self.layout_widgets()
        self.create_connections()


    def create_widgets(self, message):
        self.label = QTextBrowser()
        self.label.setStyleSheet("QTextBrowser { background: #eee; }")
        self.label.setText(message)
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)


    def layout_widgets(self):
        layout = QVBoxLayout()
        layout.addWidget(self.label, 2)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def create_connections(self):
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self.close)
