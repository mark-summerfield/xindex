#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt
from PySide.QtGui import (
    QHBoxLayout, QIcon, QLabel, QLineEdit, QToolButton, QVBoxLayout,
    QWidget)

import Lib
import Views


class SelectAllLineEdit(QLineEdit):

    def focusInEvent(self, event):
        self.selectAll()
        super().focusInEvent(event)


@Lib.updatable_tooltips
class Panel(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.helpButton.clicked.connect(
            lambda: self.state.help("xix_ref_panel_index.html"))


    def clear(self):
        self.view.clear()


    def createWidgets(self):
        self.indexLabel = QLabel("&Index ")
        self.view = Views.All.View(self.state)
        self.tooltips.append((self.view, """
<p><b>Index view</b> (Alt+I)</p>
<p>This view shows all the index's entries.</p>
<p>The entries are always shown in the correct order in accordance with
the the chosen <b>Index→Options, Rules, Calculate Sort As Rules</b>, so
there's never a need to explicitly sort.</p>"""))
        self.indexLabel.setBuddy(self.view)
        self.gotoLabel = QLabel(
            "Goto <font color=darkgreen>(Ctrl+T)</font>")
        self.gotoLineEdit = SelectAllLineEdit()
        self.gotoLabel.setBuddy(self.gotoLineEdit)
        self.tooltips.append((self.gotoLineEdit, """
<p><b>Goto (Ctrl+T)</b></p>
<p>Enter a few initial letters to goto the first main entry whose
term begins with those letters.</p>"""))
        self.state.editors.add(self.gotoLineEdit)
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.indexLabel)
        hbox.addSpacing(self.fontMetrics().width("W") * 4)
        hbox.addStretch()
        hbox.addWidget(self.gotoLabel)
        hbox.addWidget(self.gotoLineEdit, 1)
        hbox.addWidget(self.helpButton)
        layout.addLayout(hbox)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)


    def updateDisplayFonts(self):
        self.view.updateDisplayFonts()
