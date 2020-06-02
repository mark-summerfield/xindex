#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

from PySide.QtCore import Qt, QTimer
from PySide.QtGui import (
    QComboBox, QHBoxLayout, QIcon, QLabel, QToolButton, QVBoxLayout,
    QWidget)

import Lib
import Pages
import Views
from Const import FilterKind, PagesOrderKind, TOOLTIP_IMAGE_SIZE


class ComboBox(QComboBox):

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_F2:
            event.ignore()
            self.showPopup()
            return
        super().keyPressEvent(event)


    def focusInEvent(self, event):
        editor = self.lineEdit()
        if editor is not None: # Will be None if filtering by group
            editor.selectAll()
        super().focusInEvent(event)


@Lib.updatable_tooltips
class Panel(QWidget):

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.createWidgets()
        self.layoutWidgets()
        self.clear()


    def clear(self):
        self.matchTexts = []
        self.prevFilter = None
        self.view.clear()
        self.filterComboBox.setCurrentIndex(0)
        self.filterTextComboBox.clear()
        self.filterTextIndex = -1


    def createWidgets(self):
        self.helpButton = QToolButton()
        self.helpButton.setIcon(QIcon(":/help.svg"))
        self.helpButton.setFocusPolicy(Qt.NoFocus)
        self.helpButton.clicked.connect(self.help)
        self.tooltips.append((
            self.helpButton,
            """Help on the Suggestions or Filtered panel."""))
        self.view = Views.Filtered.View(self.state)
        self.tooltips.append((self.view, """<p><b>Filtered view</b></p>
<p>This view shows any entries that match the current <b>Filter</b>.</p>
<p>Press <b>F3</b> or click <img src=":/goto-found.svg" width={0}
height={0}> or click <b>Goto→Filtered</b> to go to the current filtered
entry.</p>""".format(TOOLTIP_IMAGE_SIZE)))
        self.view.match = ""
        self.filterLabel = QLabel(
            "Filter <font color=darkgreen>(Ctrl+F)</font>")
        self.filterComboBox = QComboBox()
        self.filterComboBox.setMaxVisibleItems(24)
        self.tooltips.append((self.filterComboBox, """\
<p><b>Filter combobox</b></p>
<p>Use this combobox to choose the filter to use.</p>
<p>The <b>Terms Matching</b>, <b>Pages Matching</b>, and <b>Notes
Matching</b> filters need a match text.</p>"""))
        self.filterLabel.setBuddy(self.filterComboBox)
        for filter in FilterKind:
            if not filter.isCheck:
                self.filterComboBox.addItem(filter.text, filter)
        self.filterComboBox.currentIndexChanged[int].connect(self.query)
        self.filterTextComboBox = ComboBox()
        self.filterTextComboBox.setEditable(True)
        self.filterTextComboBox.setDuplicatesEnabled(False)
        self.filterTextComboBox.currentIndexChanged[str].connect(
            self.setMatch)
        self.tooltips.append((self.filterTextComboBox, """\
<p><b>Filter Match editor</b></p>
<p>The text to match when using a <b>Terms Matching</b>, <b>Pages
Matching</b>, or <b>Notes Matching</b> filter.</p>
<p>For terms and notes, the filtered entries are chosen by
case-insensitively comparing with the match word or words.</p> <p>Add a
<tt>*</tt> after a word to match any words that begin with the text
preceding the <tt>*</tt>.</p> <p>For example, “comp*” will match
“compress”, “compulsory”, “computer”, “computed”, etc.</p>
<p>For pages, enter them as you would for an entry's pages, e.g.,
<tt>199,202-5</tt> to match entries whose pages equal or include
<tt>199,202,203,204,205</tt>, whether explicitly, or within page
ranges.</p>"""))
        self.view.pane.clickLine.connect(self.state.updateNavigationStatus)


    def layoutWidgets(self):
        layout = QVBoxLayout()
        hbox = QHBoxLayout()
        hbox.addWidget(self.filterLabel)
        hbox.addWidget(self.filterComboBox, 1)
        hbox.addWidget(self.filterTextComboBox, 2)
        hbox.addWidget(self.helpButton)
        layout.addLayout(hbox)
        layout.addWidget(self.view, 1)
        self.setLayout(layout)


    def setMatch(self, match=None):
        filter = FilterKind(self.filterComboBox.itemData(
                            self.filterComboBox.currentIndex()))
        if match is None:
            match = self.filterTextComboBox.currentText()
        arg = match
        if filter in {FilterKind.IN_NORMAL_GROUP,
                      FilterKind.IN_LINKED_GROUP,
                      FilterKind.PAGES_ORDER}:
            arg = self.filterTextComboBox.itemData(
                self.filterTextComboBox.currentIndex())
        elif filter is FilterKind.ENTRIES_WITH_PAGES:
            arg = Pages.searchablePages(match)
        self.view.query(filter, arg)
        if match:
            with Lib.BlockSignals(self.filterTextComboBox):
                index = self.filterTextComboBox.findText(match)
                if index == -1:
                    self.filterTextComboBox.addItem(match)
                    self.filterTextIndex = (
                        self.filterTextComboBox.count() - 1)
                else:
                    self.filterTextIndex = index


    def requery(self):
        filterIndex = self.filterComboBox.currentIndex()
        if -1 < self.filterTextIndex < self.filterTextComboBox.count():
            textIndex = self.filterTextIndex
        else:
            textIndex = self.filterTextComboBox.currentIndex()
        eid = self.view.selectedEid
        self.filterComboBox.setCurrentIndex(0)
        self.filterTextComboBox.setCurrentIndex(0)
        QTimer.singleShot(0, lambda index=filterIndex:
                          self.filterComboBox.setCurrentIndex(index))
        QTimer.singleShot(10, lambda index=textIndex:
                          self.filterTextComboBox.setCurrentIndex(index))
        if eid is not None:
            QTimer.singleShot(20, lambda eid=eid: self.view.gotoEid(eid))


    def query(self):
        filter = FilterKind(self.filterComboBox.itemData(
                            self.filterComboBox.currentIndex()))
        if filter in {FilterKind.IN_NORMAL_GROUP,
                      FilterKind.IN_LINKED_GROUP, FilterKind.PAGES_ORDER}:
            self._setGroupOrPagesOrder()
        elif filter in {FilterKind.ENTRIES_WITH_PAGES,
                        FilterKind.TERMS_MATCHING,
                        FilterKind.NOTES_MATCHING}:
            self.filterTextComboBox.setEditable(True)
            self.filterTextComboBox.setEnabled(True)
            if self.matchTexts:
                with Lib.BlockSignals(self.filterTextComboBox):
                    self.filterTextComboBox.clear()
                    self.filterTextComboBox.addItems(self.matchTexts)
                self.matchTexts = []
            self.setMatch()
        else:
            self.filterTextComboBox.setEnabled(False)
            self.view.query(filter)
        self.prevFilter = filter


    def _setGroupOrPagesOrder(self, gid=None):
        self.filterTextComboBox.setEditable(False)
        self.filterTextComboBox.setEnabled(True)
        items = []
        filter = FilterKind(self.filterComboBox.itemData(
                            self.filterComboBox.currentIndex()))
        if filter is FilterKind.IN_NORMAL_GROUP:
            items = list(self.state.model.normalGroups())
        elif filter is FilterKind.IN_LINKED_GROUP:
            items = list(self.state.model.linkedGroups())
        elif filter is FilterKind.PAGES_ORDER:
            items = [(int(x), x.text) for x in PagesOrderKind]
        if self.prevFilter not in {FilterKind.IN_NORMAL_GROUP,
                                   FilterKind.IN_LINKED_GROUP,
                                   FilterKind.PAGES_ORDER}:
            self.matchTexts = []
            for i in range(self.filterTextComboBox.count()):
                self.matchTexts.append(
                    self.filterTextComboBox.itemText(i))
        with Lib.BlockSignals(self.filterTextComboBox):
            index = None
            self.filterTextComboBox.clear()
            for i, (itemId, name) in enumerate(items):
                self.filterTextComboBox.addItem(name, itemId)
                if gid is not None and gid == itemId:
                    index = i
            if index is not None:
                self.filterTextComboBox.setCurrentIndex(index)
        self.setMatch()


    def updateDisplayFonts(self):
        self.view.updateDisplayFonts()


    def help(self):
        self.state.help("xix_ref_panel_filter.html")


    def setGroup(self, groupItem=None):
        if groupItem is None:
            groupItem = self.state.groupsPanel.groupsList.currentItem()
        if groupItem is not None:
            gid = groupItem.data(Qt.UserRole)
            kind = (FilterKind.IN_LINKED_GROUP
                    if self.state.model.isLinkedGroup(gid) else
                    FilterKind.IN_NORMAL_GROUP)
            for i in range(self.filterComboBox.count()):
                if FilterKind(self.filterComboBox.itemData(i)) is kind:
                    self.filterComboBox.setCurrentIndex(i)
                    break
            self._setGroupOrPagesOrder(gid)


    def groupChanged(self):
        filter = FilterKind(self.filterComboBox.itemData(
                            self.filterComboBox.currentIndex()))
        if filter in {FilterKind.IN_NORMAL_GROUP,
                      FilterKind.IN_LINKED_GROUP}:
            self.view.refresh()
