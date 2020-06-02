#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings
from PySide.QtGui import (
    QCheckBox, QFont, QFormLayout, QGridLayout, QHBoxLayout, QLabel,
    QWidget)

from Config import Gopt
import Lib
from Const import WIN


class Panel(QWidget):

    def __init__(self, state, config, parent):
        super().__init__(parent)
        self.state = state
        self.config = config
        self.form = parent
        self.createWidgets()
        self.layoutWidgets()
        self.createConnections()


    def createWidgets(self):
        size = self.font().pointSize() + (1 if WIN else 2)
        Lib.createFontBoxesFor(
            self, "DisplayStd", *self.getFontFamilyAndSize(
                Gopt.Key.StdFont, Gopt.StdFont, Gopt.Key.StdFontSize, size),
            tooltips=self.form.tooltips, which="Std.")
        self.onDisplayStdFontChange(False)
        Lib.createFontBoxesFor(
            self, "DisplayAlt", *self.getFontFamilyAndSize(
                Gopt.Key.AltFont, Gopt.AltFont, Gopt.Key.AltFontSize, size),
            tooltips=self.form.tooltips, which="Alt.")
        self.onDisplayAltFontChange(False)
        Lib.createFontBoxesFor(
            self, "DisplayMono", *self.getFontFamilyAndSize(
                Gopt.Key.MonoFont, Gopt.MonoFont, Gopt.Key.MonoFontSize,
                size - 1),
            mono=True, tooltips=self.form.tooltips, which="Mono.")
        self.onDisplayMonoFontChange(False)

        settings = QSettings()

        index = int(settings.value(Gopt.Key.MainForm_IndexViewPosition,
                                   Gopt.Default.MainForm_IndexViewPosition))
        self.indexViewOnLeft = QCheckBox("&Index View on Left")
        self.indexViewOnLeft.setChecked(not index)
        self.form.tooltips.append((self.indexViewOnLeft, """\
<p><b>Index View on Left</b></p>
<p>If checked, the index view will appear on the left with the entry,
suggestions, and filtered panels on the right.</p>"""))

        showNotes = bool(int(settings.value(Gopt.Key.ShowNotes,
                                            Gopt.Default.ShowNotes)))
        self.showNotesCheckBox = QCheckBox("Show &Notes")
        self.showNotesCheckBox.setChecked(showNotes)
        self.form.tooltips.append((self.showNotesCheckBox, """\
<p><b>Show Notes</b></p>
<p>If checked, a notes edit&mdash;and any notes that have been
entered&mdash; is visible in the entry panel.</p>"""))

        alwaysShowSortAs = bool(int(settings.value(
            Gopt.Key.AlwaysShowSortAs, Gopt.Default.AlwaysShowSortAs)))
        self.alwaysShowSortAsCheckBox = QCheckBox("A&lways Show Sort As")
        self.alwaysShowSortAsCheckBox.setChecked(alwaysShowSortAs)
        self.form.tooltips.append((self.alwaysShowSortAsCheckBox, """\
<p><b>Always Show Sort As</b></p>
<p>If checked, every entry's sort as text is shown. If unchecked,  the
sort as text is only shown if it is entered manually, i.e., if the
<b>Automatically Calculate Sort As</b> checkbox is checked.</p>"""))

        showMenuToolTips = bool(int(settings.value(
            Gopt.Key.ShowMenuToolTips, Gopt.Default.ShowMenuToolTips)))
        self.showMenuToolTipsCheckBox = QCheckBox("Show Menu &Tooltips")
        self.showMenuToolTipsCheckBox.setChecked(showMenuToolTips)
        self.form.tooltips.append((self.showMenuToolTipsCheckBox, """\
<p><b>Show Menu Tooltips</b></p>
<p>If checked, menu tooltips are shown when menus are pulled down and
navigated using the mouse or keyboard.</p>"""))

        showMainWindowToolTips = bool(int(settings.value(
            Gopt.Key.ShowMainWindowToolTips,
            Gopt.Default.ShowMainWindowToolTips)))
        self.showMainWindowToolTipsCheckBox = QCheckBox(
            "Show Main &Window Tooltips")
        self.showMainWindowToolTipsCheckBox.setChecked(
            showMainWindowToolTips)
        self.form.tooltips.append((self.showMainWindowToolTipsCheckBox, """\
<p><b>Show Main Window Tooltips</b></p>
<p>If checked, tooltips are shown when the mouse hovers over controls in
the main window.</p>"""))

        showDialogToolTips = bool(int(settings.value(
            Gopt.Key.ShowDialogToolTips, Gopt.Default.ShowDialogToolTips)))
        self.showDialogToolTipsCheckBox = QCheckBox("Show &Dialog Tooltips")
        self.showDialogToolTipsCheckBox.setChecked(showDialogToolTips)
        self.form.tooltips.append((self.showDialogToolTipsCheckBox, """\
<p><b>Show Dialog Tooltips</b></p>
<p>If checked, tooltips are shown when the mouse hovers over controls in
dialogs (such as this one).</p>"""))

        keepHelpOnTop = bool(int(settings.value(
            Gopt.Key.KeepHelpOnTop, Gopt.Default.KeepHelpOnTop)))
        self.keepHelpOnTopCheckBox = QCheckBox("Keep &Help on Top")
        self.keepHelpOnTopCheckBox.setChecked(keepHelpOnTop)
        self.form.tooltips.append((self.keepHelpOnTopCheckBox, """\
<p><b>Keep Help on Top</b></p>
<p>If checked, when you pop up the help window it will stay above any
other XindeX window, even if you click another XindeX window.</p>"""))

        showSplash = bool(int(settings.value(Gopt.Key.ShowSplash,
                                             Gopt.Default.ShowSplash)))
        self.showSplashCheckBox = QCheckBox("Show S&plash at Startup")
        self.showSplashCheckBox.setChecked(showSplash)
        self.form.tooltips.append((self.showSplashCheckBox, """\
<p><b>Show Splash at Startup</b></p>
<p>If checked, a splash window showing the XindeX icon and name will appear
while XindeX is starting.</p>"""))


    def layoutWidgets(self):
        form = QFormLayout()
        grid = QGridLayout()
        grid.addWidget(self.indexViewOnLeft, 0, 0)
        grid.addWidget(self.alwaysShowSortAsCheckBox, 1, 0)
        grid.addWidget(self.showNotesCheckBox, 2, 0)
        grid.addWidget(self.showMenuToolTipsCheckBox, 0, 1)
        grid.addWidget(self.showMainWindowToolTipsCheckBox, 1, 1)
        grid.addWidget(self.showDialogToolTipsCheckBox, 2, 1)
        grid.addWidget(self.keepHelpOnTopCheckBox, 3, 1)
        grid.addWidget(self.showSplashCheckBox, 4, 1)
        hbox = QHBoxLayout()
        hbox.addLayout(grid)
        hbox.addStretch()
        form.addRow(hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.displaystdFontComboBox, 1)
        hbox.addWidget(self.displaystdFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Std. Font")
        label.setBuddy(self.displaystdFontComboBox)
        form.addRow(label, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.displayaltFontComboBox, 1)
        hbox.addWidget(self.displayaltFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Alt. Font")
        label.setBuddy(self.displayaltFontComboBox)
        form.addRow(label, hbox)
        hbox = QHBoxLayout()
        hbox.addWidget(self.displaymonoFontComboBox, 1)
        hbox.addWidget(self.displaymonoFontSizeSpinBox)
        hbox.addStretch()
        label = QLabel("&Mono. Font")
        label.setBuddy(self.displaymonoFontComboBox)
        form.addRow(label, hbox)
        self.setLayout(form)


    def createConnections(self):
        self.displaystdFontComboBox.currentFontChanged.connect(
            self.onDisplayStdFontChange)
        self.displaystdFontSizeSpinBox.valueChanged[int].connect(
            self.onDisplayStdFontChange)
        self.displayaltFontComboBox.currentFontChanged.connect(
            self.onDisplayAltFontChange)
        self.displayaltFontSizeSpinBox.valueChanged[int].connect(
            self.onDisplayAltFontChange)
        self.displaymonoFontComboBox.currentFontChanged.connect(
            self.onDisplayMonoFontChange)
        self.displaymonoFontSizeSpinBox.valueChanged[int].connect(
            self.onDisplayMonoFontChange)
        self.indexViewOnLeft.stateChanged.connect(self.setIndexViewOnLeft)
        self.showNotesCheckBox.stateChanged.connect(self.setShowNotes)
        self.alwaysShowSortAsCheckBox.stateChanged.connect(
            self.setAlwaysShowSortAs)
        self.showMenuToolTipsCheckBox.stateChanged.connect(
            self.setShowMenuToolTips)
        self.showMainWindowToolTipsCheckBox.stateChanged.connect(
            self.setShowMainWindowToolTips)
        self.showDialogToolTipsCheckBox.stateChanged.connect(
            self.setShowDialogToolTips)
        self.showSplashCheckBox.stateChanged.connect(self.setShowSplash)
        self.keepHelpOnTopCheckBox.stateChanged.connect(
            self.setKeepHelpOnTop)


    def getFontFamilyAndSize(self, familyOpt, familyDef, sizeOpt, sizeDef):
        settings = QSettings()
        family = settings.value(familyOpt, familyDef)
        size = int(settings.value(sizeOpt, sizeDef))
        return family, size


    def onDisplayStdFontChange(self, propagate=True):
        font = QFont(self.displaystdFontComboBox.currentFont())
        font.setPointSize(self.displaystdFontSizeSpinBox.value())
        if propagate:
            settings = QSettings()
            settings.setValue(Gopt.Key.StdFont, font.family())
            settings.setValue(Gopt.Key.StdFontSize, font.pointSize())
            self.state.updateDisplayFonts()


    def onDisplayAltFontChange(self, propagate=True):
        font = QFont(self.displayaltFontComboBox.currentFont())
        font.setPointSize(self.displayaltFontSizeSpinBox.value())
        if propagate:
            settings = QSettings()
            settings.setValue(Gopt.Key.AltFont, font.family())
            settings.setValue(Gopt.Key.AltFontSize, font.pointSize())
            self.state.updateDisplayFonts()


    def onDisplayMonoFontChange(self, propagate=True):
        font = QFont(self.displaymonoFontComboBox.currentFont())
        font.setPointSize(self.displaymonoFontSizeSpinBox.value())
        if propagate:
            settings = QSettings()
            settings.setValue(Gopt.Key.MonoFont, font.family())
            settings.setValue(Gopt.Key.MonoFontSize, font.pointSize())
            self.state.updateDisplayFonts()


    def setIndexViewOnLeft(self):
        index = 0 if self.indexViewOnLeft.isChecked() else 1
        settings = QSettings()
        settings.setValue(Gopt.Key.MainForm_IndexViewPosition, index)
        self.state.window.setIndexViewPosition()


    def setShowNotes(self):
        showNotes = int(self.showNotesCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.ShowNotes, showNotes)
        self.state.entryPanel.showOrHideNotes()


    def setAlwaysShowSortAs(self):
        alwaysShowSortAs = int(self.alwaysShowSortAsCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.AlwaysShowSortAs, alwaysShowSortAs)
        self.state.entryPanel.showOrHideSortAs()


    def setShowMenuToolTips(self):
        showMenuToolTips = int(self.showMenuToolTipsCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.ShowMenuToolTips, showMenuToolTips)


    def setShowMainWindowToolTips(self):
        showMainWindowToolTips = int(
            self.showMainWindowToolTipsCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.ShowMainWindowToolTips,
                          showMainWindowToolTips)
        self.state.window.updateToolTips()


    def setShowDialogToolTips(self):
        showDialogToolTips = int(
            self.showDialogToolTipsCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.ShowDialogToolTips, showDialogToolTips)
        self.form.updateToolTips(showDialogToolTips)


    def setShowSplash(self):
        showSplash = int(self.showSplashCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.ShowSplash, showSplash)


    def setKeepHelpOnTop(self):
        keepHelpOnTop = int(self.keepHelpOnTopCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.KeepHelpOnTop, keepHelpOnTop)
