#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import QSettings, Qt
from PySide.QtGui import (
    QCheckBox, QComboBox, QFormLayout, QGroupBox, QHBoxLayout, QLabel,
    QSpinBox, QVBoxLayout, QWidget)

from Config import Gconf, Gopt
import Pages
import SortAs


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
        settings = QSettings()
        self.sortRulesGroupBox = QGroupBox("Calculate &Sort As Rules")
        defaultSortAsRules = settings.value(Gconf.Key.SortAsRules,
                                            Gopt.Default.SortAsRules)
        self.thisSortAsRules = self.config.get(Gopt.Key.SortAsRules,
                                               defaultSortAsRules)
        self.defaultSortAsRulesBox = QComboBox()
        self.form.tooltips.append((self.defaultSortAsRulesBox, """\
<p><b>Calculate Sort As Rules, Default</b></p>
<p>The default setting for the <b>Calculate Sort As Rules, For This
Index</b> combobox for new indexes.</p>"""))
        self.thisSortAsRulesBox = QComboBox()
        self.form.tooltips.append((self.thisSortAsRulesBox, """\
<p><b>Calculate Sort As Rules, For This Index</b></p>
<p>The rules to use for calculating each entry's sort as text for this
index.</p>
<p>If the rules are changed, when the dialog is closed, the new rules
will be applied to every entry in the index.</p>"""))
        self.populateSortAsRulesBox(self.defaultSortAsRulesBox,
                                    defaultSortAsRules)
        self.populateSortAsRulesBox(self.thisSortAsRulesBox,
                                    self.thisSortAsRules)

        self.pageRangeRulesBox = QGroupBox("&Page Range Rules")
        defaultPageRangeRules = settings.value(Gconf.Key.PageRangeRules,
                                               Gopt.Default.PageRangeRules)
        self.thisPageRangeRules = self.config.get(Gopt.Key.PageRangeRules,
                                                  defaultPageRangeRules)
        self.defaultPageRangeRulesBox = QComboBox()
        self.form.tooltips.append((self.defaultPageRangeRulesBox, """\
<p><b>Page Range Rules, Default</b></p>
<p>The default setting for the <b>Page Range Rules, For This Index</b>
combobox for new indexes.</p>"""))
        self.thisPageRangeRulesBox = QComboBox()
        self.form.tooltips.append((self.thisPageRangeRulesBox, """\
<p><b>Page Range Rules, For This Index</b></p>
<p>The rules to use for handling page ranges, e.g., whether in full such
as 120&ndash;124, or somehow compressed, e.g., 120&ndash;4, for this
index.</p>
<p>If the rules are changed, when the dialog is closed, the new rules
will be applied to every entry in the index.</p>"""))
        self.populatePageRangeRulesBox(self.defaultPageRangeRulesBox,
                                       defaultPageRangeRules)
        self.populatePageRangeRulesBox(self.thisPageRangeRulesBox,
                                       self.thisPageRangeRules)
        self.padDigitsGroupBox = QGroupBox("Pad &Digits")
        defaultPadDigits = int(settings.value(Gconf.Key.PadDigits,
                                              Gopt.Default.PadDigits))
        self.thisPadDigits = int(self.config.get(Gopt.Key.PadDigits,
                                                 defaultPadDigits))
        self.thisPadDigitsLabel = QLabel("For This Index")
        self.thisPadDigitsSpinBox = QSpinBox()
        self.thisPadDigitsSpinBox.setAlignment(Qt.AlignRight)
        self.thisPadDigitsSpinBox.setRange(0, 12)
        self.thisPadDigitsSpinBox.setValue(self.thisPadDigits)
        self.form.tooltips.append((self.thisPadDigitsSpinBox, """\
<p><b>Pad Digits, For This Index</b></p>
<p>Sort as texts are compared textually, so if a term contains a number
(or text which is converted to a number), the number must be padded by
leading zeros to ensure correct ordering. This is the number of digits
to pad for, for this index. For example, if set to 4, the numbers 1, 23,
and 400 would be set to 0001, 0023, and 0400, in the sort as text.</p>"""))
        self.defaultPadDigitsLabel = QLabel("Default")
        self.defaultPadDigitsSpinBox = QSpinBox()
        self.defaultPadDigitsSpinBox.setAlignment(Qt.AlignRight)
        self.defaultPadDigitsSpinBox.setRange(0, 12)
        self.defaultPadDigitsSpinBox.setValue(defaultPadDigits)
        self.form.tooltips.append((self.defaultPadDigitsSpinBox, """\
<p><b>Pad Digits, Default</b></p>
<p>The default setting for the <b>Pad Digits, For This Index</b> spinbox
for new indexes.</p>"""))
        self.ignoreSubFirstsGroupBox = QGroupBox(
            "&Ignore Subentry Function Words")
        defaultIgnoreSubFirsts = bool(int(settings.value(
            Gconf.Key.IgnoreSubFirsts, Gopt.Default.IgnoreSubFirsts)))
        thisIgnoreSubFirsts = bool(int(self.config.get(
            Gopt.Key.IgnoreSubFirsts, defaultIgnoreSubFirsts)))
        self.thisIgnoreSubFirstsCheckBox = QCheckBox("For This Index")
        self.thisIgnoreSubFirstsCheckBox.setChecked(thisIgnoreSubFirsts)
        self.form.tooltips.append((self.thisIgnoreSubFirstsCheckBox, """\
<p><b>Ignore Subentry Function Words, For This Index</b></p>
<p>This setting applies to this index.</p>
<p>If checked, words listed in the <b>Index→Ignore Subentry Function
Words</b> list are ignored for sorting purposes when the first word of a
subentry, i.e., ignored when the first word of an entry's sort as
text.</p> <p>This should normally be checked for Chicago Manual of Style
Sort As Rules, and unchecked for NISO Rules.</p>"""))
        self.defaultIgnoreSubFirstsCheckBox = QCheckBox("Default")
        self.defaultIgnoreSubFirstsCheckBox.setChecked(
            defaultIgnoreSubFirsts)
        self.form.tooltips.append((self.defaultIgnoreSubFirstsCheckBox, """\
<p><b>Ignore Subentry Function Words, Default</b></p>
<p>The default setting for the <b>Ignore Subentry Function Words, For
This Index</b> checkbox for new indexes</p>"""))
        self.suggestSpelledGroupBox = QGroupBox(
            "&Suggest Spelled Out Numbers when Appropriate")
        defaultSuggestSpelled = bool(int(settings.value(
            Gconf.Key.SuggestSpelled, Gopt.Default.SuggestSpelled)))
        thisSuggestSpelled = bool(int(self.config.get(
            Gopt.Key.SuggestSpelled, defaultSuggestSpelled)))
        self.thisSuggestSpelledCheckBox = QCheckBox("For This Index")
        self.thisSuggestSpelledCheckBox.setChecked(thisSuggestSpelled)
        self.form.tooltips.append((self.thisSuggestSpelledCheckBox, """\
<p><b>Suggest Spelled Out Numbers when Appropriate, For This Index</b></p>
<p>When checked (and providing the Sort As rules in force are not NISO
rules), when adding or editing a term when the <b>Automatically
Calculate Sort As</b> checkbox is checked, and when the term contains a
number, the choice of sort as texts will include the number spelled
out.</p>"""))
        self.defaultSuggestSpelledCheckBox = QCheckBox("Default")
        self.defaultSuggestSpelledCheckBox.setChecked(
            defaultSuggestSpelled)
        self.form.tooltips.append((self.defaultSuggestSpelledCheckBox, """\
<p><b>Suggest Spelled Out Numbers when Appropriate, Default</b></p>
<p>The default setting for the <b>Suggest Spelled Out Numbers when
Appropriate, For This Index</b> checkbox for new indexes.</p>"""))


    def layoutWidgets(self):
        layout = QVBoxLayout()

        form = QFormLayout()
        form.addRow("For This Index", self.thisSortAsRulesBox)
        form.addRow("Default", self.defaultSortAsRulesBox)
        self.sortRulesGroupBox.setLayout(form)
        layout.addWidget(self.sortRulesGroupBox)

        form = QFormLayout()
        form.addRow("For This Index", self.thisPageRangeRulesBox)
        form.addRow("Default", self.defaultPageRangeRulesBox)
        self.pageRangeRulesBox.setLayout(form)
        layout.addWidget(self.pageRangeRulesBox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.thisPadDigitsLabel)
        hbox.addWidget(self.thisPadDigitsSpinBox)
        hbox.addStretch(1)
        hbox.addWidget(self.defaultPadDigitsLabel)
        hbox.addWidget(self.defaultPadDigitsSpinBox)
        hbox.addStretch(3)
        self.padDigitsGroupBox.setLayout(hbox)
        layout.addWidget(self.padDigitsGroupBox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.thisIgnoreSubFirstsCheckBox)
        hbox.addWidget(self.defaultIgnoreSubFirstsCheckBox)
        hbox.addStretch()
        self.ignoreSubFirstsGroupBox.setLayout(hbox)
        layout.addWidget(self.ignoreSubFirstsGroupBox)

        hbox = QHBoxLayout()
        hbox.addWidget(self.thisSuggestSpelledCheckBox)
        hbox.addWidget(self.defaultSuggestSpelledCheckBox)
        hbox.addStretch()
        self.suggestSpelledGroupBox.setLayout(hbox)
        layout.addWidget(self.suggestSpelledGroupBox)

        layout.addStretch()
        self.setLayout(layout)


    def createConnections(self):
        self.defaultSortAsRulesBox.currentIndexChanged.connect(
            self.setDefaultSortAsRules)
        self.defaultPageRangeRulesBox.currentIndexChanged.connect(
            self.setDefaultPageRangeRules)
        self.defaultPadDigitsSpinBox.valueChanged.connect(
            self.setDefaultPadDigits)
        self.defaultIgnoreSubFirstsCheckBox.toggled.connect(
            self.setDefaultIgnoreSubFirsts)
        self.defaultSuggestSpelledCheckBox.toggled.connect(
            self.setDefaultSuggestSpelled)


    def populateSortAsRulesBox(self, combobox, rules):
        index = -1
        for i, name in enumerate(SortAs.RulesForName):
            displayName = SortAs.RulesForName[name].name
            combobox.addItem(displayName, name)
            if name == rules:
                index = i
        combobox.setCurrentIndex(index)


    def setDefaultSortAsRules(self, index):
        index = self.defaultSortAsRulesBox.currentIndex()
        name = self.defaultSortAsRulesBox.itemData(index)
        settings = QSettings()
        settings.setValue(Gopt.Key.SortAsRules, name)


    def populatePageRangeRulesBox(self, combobox, rules):
        index = -1
        for i, name in enumerate(Pages.RulesForName):
            displayName = Pages.RulesForName[name].name
            combobox.addItem(displayName, name)
            if name == rules:
                index = i
        combobox.setCurrentIndex(index)


    def setDefaultPageRangeRules(self, index):
        index = self.defaultPageRangeRulesBox.currentIndex()
        name = self.defaultPageRangeRulesBox.itemData(index)
        settings = QSettings()
        settings.setValue(Gopt.Key.PageRangeRules, name)


    def setDefaultPadDigits(self):
        value = self.defaultPadDigitsSpinBox.value()
        settings = QSettings()
        settings.setValue(Gopt.Key.PadDigits, value)


    def setDefaultIgnoreSubFirsts(self):
        value = int(self.defaultIgnoreSubFirstsCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.IgnoreSubFirsts, value)


    def setDefaultSuggestSpelled(self):
        value = int(self.defaultSuggestSpelledCheckBox.isChecked())
        settings = QSettings()
        settings.setValue(Gopt.Key.SuggestSpelled, value)
