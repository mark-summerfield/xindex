#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

if __name__ == "__main__":
    import os
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QApplication, QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QIcon, QLabel, QPushButton, QSpinBox, QVBoxLayout)

import Lib
import Widgets
from Config import Gopt
from Const import RenumberOptions, say, SAY_TIMEOUT


@Lib.updatable_tooltips
class Form(QDialog):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        Lib.prepareModalDialog(self)
        self.state = state
        self.setWindowTitle("Renumber Pages — {}".format(
                            QApplication.applicationName()))
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()
        self.romanStartSpinBox.setFocus()
        self.updateUi()
        settings = QSettings()
        self.updateToolTips(bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips))))


    def createWidgets(self):
        self.romanStartLabel = QLabel("&Roman from")
        self.romanStartSpinBox = Widgets.RomanSpinBox.SpinBox()
        self.tooltips.append((self.romanStartSpinBox, """\
<p><b>Roman from</b></p>
<p>The first roman page number to change.</p>"""))
        self.romanStartLabel.setBuddy(self.romanStartSpinBox)
        self.romanEndLabel = QLabel("to")
        self.romanEndSpinBox = Widgets.RomanSpinBox.SpinBox()
        self.romanEndSpinBox.setValue(200)
        self.tooltips.append((self.romanEndSpinBox, """\
<p><b>Roman, to</b></p>
<p>The last roman page number to change.</p>"""))
        self.romanChangeLabel = QLabel("change")
        self.romanChangeSpinBox = Widgets.ChangeSpinBox.SpinBox()
        self.romanChangeSpinBox.setRange(-100, 100)
        self.romanChangeSpinBox.setValue(0)
        self.romanChangeSpinBox.setMinimumWidth(
            self.romanChangeSpinBox.fontMetrics().width("W(no change)W"))
        self.tooltips.append((self.romanChangeSpinBox, """\
<p><b>Roman, change</b></p>
<p>The amount to change the roman page numbers in the Roman from&ndash;to
range.</p>"""))
        self.decimalStartLabel = QLabel("&Decimal from")
        self.decimalStartSpinBox = QSpinBox()
        self.decimalStartSpinBox.setAlignment(Qt.AlignRight)
        self.decimalStartLabel.setBuddy(self.decimalStartSpinBox)
        self.decimalStartSpinBox.setRange(1, 10000)
        self.tooltips.append((self.decimalStartSpinBox, """\
<p><b>Decimal from</b></p>
<p>The first decimal page number to change.</p>"""))
        self.decimalEndLabel = QLabel("to")
        self.decimalEndSpinBox = QSpinBox()
        self.decimalEndSpinBox.setAlignment(Qt.AlignRight)
        self.decimalEndSpinBox.setRange(1, 10000)
        self.decimalEndSpinBox.setValue(2000)
        self.tooltips.append((self.decimalEndSpinBox, """\
<p><b>Decimal, to</b></p>
<p>The last decimal page number to change.</p>"""))
        self.decimalChangeLabel = QLabel("change")
        self.decimalChangeSpinBox = Widgets.ChangeSpinBox.SpinBox()
        self.decimalChangeSpinBox.setRange(-100, 100)
        self.decimalChangeSpinBox.setValue(0)
        self.tooltips.append((self.decimalChangeSpinBox, """\
<p><b>Decimal, change</b></p>
<p>The amount to change the decimal page numbers in the Decimal
from&ndash;to range.</p>"""))

        self.buttonBox = QDialogButtonBox()
        self.renumberButton = QPushButton(QIcon(":/renumberpages.svg"),
                                          "Re&number")
        self.tooltips.append((self.renumberButton, """\
<p><b>Renumber</b></p>
<p>Renumber roman and decimal page numbers within the given ranges by
the specified amounts of change throughout the entire index.</p>"""))
        self.buttonBox.addButton(self.renumberButton,
                                 QDialogButtonBox.ActionRole)
        self.closeButton = QPushButton(QIcon(":/dialog-close.svg"),
                                       "&Cancel")
        self.tooltips.append((self.closeButton, """<p><b>Cancel</b></p>
<p>Close the dialog without making any changes to the index.</p>"""))
        self.buttonBox.addButton(self.closeButton,
                                 QDialogButtonBox.RejectRole)
        self.helpButton = QPushButton(QIcon(":/help.svg"), "Help")
        self.tooltips.append((self.helpButton,
                              "Help on the Renumber Pages dialog"))
        self.buttonBox.addButton(self.helpButton,
                                 QDialogButtonBox.HelpRole)


    def layoutWidgets(self):
        grid = QGridLayout()
        grid.addWidget(self.romanStartLabel, 0, 0)
        grid.addWidget(self.romanStartSpinBox, 0, 1)
        grid.addWidget(self.romanEndLabel, 0, 2)
        grid.addWidget(self.romanEndSpinBox, 0, 3)
        grid.addWidget(self.romanChangeLabel, 0, 4)
        grid.addWidget(self.romanChangeSpinBox, 0, 5)
        grid.addWidget(self.decimalStartLabel, 1, 0)
        grid.addWidget(self.decimalStartSpinBox, 1, 1)
        grid.addWidget(self.decimalEndLabel, 1, 2)
        grid.addWidget(self.decimalEndSpinBox, 1, 3)
        grid.addWidget(self.decimalChangeLabel, 1, 4)
        grid.addWidget(self.decimalChangeSpinBox, 1, 5)
        hbox = QHBoxLayout()
        hbox.addLayout(grid)
        hbox.addStretch()
        layout = QVBoxLayout()
        layout.addLayout(hbox)
        layout.addStretch()
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)


    def createConnections(self):
        self.buttonBox.rejected.connect(self.reject)
        self.renumberButton.clicked.connect(self.renumber)
        for spinbox in (self.romanStartSpinBox, self.romanEndSpinBox,
                        self.romanChangeSpinBox, self.decimalStartSpinBox,
                        self.decimalEndSpinBox, self.decimalChangeSpinBox):
            spinbox.valueChanged.connect(self.updateUi)
        self.helpButton.clicked.connect(self.help)


    def updateUi(self):
        self._synchronize(self.romanStartSpinBox, self.romanEndSpinBox)
        self._synchronize(self.decimalStartSpinBox, self.decimalEndSpinBox)
        changeRoman = ((self.romanStartSpinBox.value() !=
                        self.romanEndSpinBox.value()) and
                       self.romanChangeSpinBox.value() != 0)
        changeDecimal = ((self.decimalStartSpinBox.value() !=
                          self.decimalEndSpinBox.value()) and
                         self.decimalChangeSpinBox.value() != 0)
        self.renumberButton.setEnabled(changeRoman or changeDecimal)
        self._setPrefix(self.romanChangeSpinBox)
        self._setPrefix(self.decimalChangeSpinBox)


    def _synchronize(self, startSpinBox, endSpinBox):
        value = startSpinBox.value()
        if endSpinBox.value() < value:
            endSpinBox.setValue(value)


    def _setPrefix(self, spinbox):
        spinbox.setPrefix("+" if spinbox.value() > 0 else "")


    def help(self):
        self.state.help("xix_ref_dlg_renumpages.html")


    def renumber(self): # No need to restore focus widget
        options = RenumberOptions(
            self.romanStartSpinBox.value(),
            self.romanEndSpinBox.value(),
            self.romanChangeSpinBox.value(),
            self.decimalStartSpinBox.value(),
            self.decimalEndSpinBox.value(),
            self.decimalChangeSpinBox.value())
        with Lib.DisableUI(self):
            self.state.model.renumber(options,
                                      self.state.window.reportProgress)
        message = "Renumber pages"
        if self.state.model.canUndo:
            self.state.model.can_undo.emit(True, message)
        if self.state.model.canRedo:
            self.state.model.can_redo.emit(True, message)
        self.state.updateUi()
        say("Renumbered pages", SAY_TIMEOUT)
        self.accept()


if __name__ == "__main__":
    import collections
    import Qrc # noqa
    import HelpForm
    Entry = collections.namedtuple("Entry", "eid saf sortas term pages")
    class FakeModel:
        def __init__(self):
            class E:
                def emit(self, *args):
                    pass
            self.can_undo = E()
            self.can_redo = E()
        def canUndo(self):
            return False
        def canRedo(self):
            return False
        def renumber(self, options, reportProgress):
            print("renumber", options)
    class FakeView:
        def __init__(self):
            self.selectedEid = 88
    class FakePanel:
        def __init__(self):
            self.view = FakeView()
    class FakeWindow:
        def reportProgress(self, *args):
            pass
    class FakeState:
        def __init__(self):
            self.model = FakeModel()
            self.viewAllPanel = FakePanel()
            self.stdFontFamily = "Times New Roman"
            self.stdFontSize = 13
            self.altFontFamily = "Arial"
            self.altFontSize = 13
            self.monoFontFamily = "Courier New"
            self.monoFontSize = 12
            self.window = FakeWindow()
            self.helpForm = None
        def help(self, page=None):
            if self.helpForm is None:
                self.helpForm = HelpForm.Form("xix_help.html")
            if page is not None:
                self.helpForm.changePage(page)
            self.helpForm.show()
            self.helpForm.raise_()
            self.helpForm.activateWindow()
        def updateUi(self):
            pass
    app = QApplication([])
    app.setOrganizationName("Qtrac Ltd.")
    app.setOrganizationDomain("qtrac.eu")
    app.setApplicationName("XindeX-Test")
    app.setApplicationVersion("1.0.0")
    state = FakeState()
    form = Form(state)
    form.show()
    app.exec_()
