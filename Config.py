#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import sys
import types

from PySide.QtCore import QSize

from Const import (
    DEFAULT_PAD_DIGITS, IndentKind, LanguageKind, PaperSizeKind,
    SeeAlsoPositionKind, StyleKind, XRefToSubentryKind)

_USE_DEFAULT = object()


class Config:

    def __init__(self):
        self.Default = types.SimpleNamespace()


    def get(self, key, default=_USE_DEFAULT):
        if default is _USE_DEFAULT:
            default = getattr(self.Default, key, None)
        return getattr(self, key, default)


    def __iter__(self):
        for key in sorted(dir(self)):
            if not key.startswith("_"):
                value = getattr(self, key)
                if (not callable(value) and
                        not isinstance(value, types.SimpleNamespace)):
                    yield (key, value)


    def copy(self):
        config = self.__class__()
        for key, value in self:
            setattr(config, key, value)
        return config


    def _dump(self, file=sys.stdout):
        for key, value in self:
            print("{}: {!r}".format(key, value), file=file)


# Always prefer Gopt.Default.* (options) to Gconf.Default.* (config)

def _make_config(): # Per .xix
    config = Config()
    config.Default.Creator = ""
    config.Default.Initials = ""
    config.Default.Language = LanguageKind.AMERICAN
    config.Default.Indent = IndentKind.TAB
    config.Default.TermPagesSeparator = ", " # Note trailing space
    config.Default.StdFont = "Times New Roman"
    config.Default.StdFontSize = 10
    config.Default.AltFont = "Arial"
    config.Default.AltFontSize = 9
    config.Default.MonoFont = "Courier New"
    config.Default.MonoFontSize = 9
    config.Default.MonoFontAsStrikeout = False
    config.Default.SortAsRules = "wordByWordNISO3"
    config.Default.PageRangeRules = "pageRangeCMS16"
    config.Default.Worktime = 0
    config.Default.XRefToSubentry = XRefToSubentryKind.COLON
    config.Default.See = "<i>See</i> " # Note trailing space
    config.Default.SeePrefix = ". "
    config.Default.SeeSuffix = ""
    config.Default.SeeSeparator = "; "
    config.Default.SeeAlso = "<i>See also</i> " # Note trailing space
    config.Default.SeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
    config.Default.SeeAlsoPrefix = ". "
    config.Default.SeeAlsoSuffix = ""
    config.Default.SeeAlsoSeparator = "; "
    config.Default.GenericConjunction = " and "
    config.Default.SubSee = "<i>see</i> " # Note trailing space
    config.Default.SubSeePrefix = " ("
    config.Default.SubSeeSuffix = ")"
    config.Default.SubSeeSeparator = "; "
    config.Default.SubSeeAlso = "<i>see also</i> " # Note trailing space
    config.Default.SubSeeAlsoPosition = SeeAlsoPositionKind.AFTER_PAGES
    config.Default.SubSeeAlsoPrefix = " ("
    config.Default.SubSeeAlsoSuffix = ")"
    config.Default.SubSeeAlsoSeparator = "; "
    config.Default.Title = "Index"
    config.Default.Note = ""
    config.Default.SectionPreLines = 1
    config.Default.SectionPostLines = 1
    config.Default.SectionTitles = True
    config.Default.SectionSpecialTitle = """<span style="font-size: \
11pt; font-family: 'Arial';"><b>Symbols &amp; Numbers</b></span>"""
    config.Default.Style = StyleKind.INDENTED
    config.Default.RunInSeparator = "; "
    config.Default.PadDigits = DEFAULT_PAD_DIGITS
    config.Default.IgnoreSubFirsts = True
    config.Default.SuggestSpelled = True
    config.Default.HighestPageNumber = 1999
    config.Default.LargestPageRange = 10
    config.Default.MostPages = 10
    return _add_keys_and_values(config)


def _make_options(): # Global QSettings
    options = Config()
    options.Default = types.SimpleNamespace()
    options.Default.Creator = ""
    options.Default.Initials = ""
    options.Default.Language = LanguageKind.AMERICAN
    options.Default.ShowNotes = 1
    options.Default.AlwaysShowSortAs = 0
    options.Default.MainForm_IndexViewPosition = 1
    options.Default.MainForm_Filename = None
    options.Default.MainForm_Geometry = None
    options.Default.MainForm_State = None
    options.Default.MainForm_Splitter = None
    options.Default.MainForm_PanelSplitter = None
    options.Default.MainForm_EntrySuggestionsSplitter = None
    options.Default.MainForm_SpellAndGroupsSplitter = None
    options.Default.MainForm_ViewSplitter = None
    options.Default.MainForm_RecentFiles = None
    options.Default.CheckForm_Size = QSize(640, 480)
    options.Default.SortAsRules = "wordByWordNISO3"
    options.Default.PageRangeRules = "pageRangeCMS16"
    options.Default.StdFont = "Times New Roman"
    options.Default.StdFontSize = 10
    options.Default.AltFont = "Arial"
    options.Default.AltFontSize = 9
    options.Default.MonoFont = "Courier New"
    options.Default.MonoFontSize = 9
    options.Default.PaperSize = PaperSizeKind.LETTER
    options.Default.PadDigits = DEFAULT_PAD_DIGITS
    options.Default.IgnoreSubFirsts = True
    options.Default.SuggestSpelled = True
    options.Default.ShowMenuToolTips = 1
    options.Default.ShowMainWindowToolTips = 1
    options.Default.ShowDialogToolTips = 1
    options.Default.ShowSplash = 1
    options.Default.KeepHelpOnTop = 1
    options.Default.IndentRTF = IndentKind.TAB
    return _add_keys_and_values(options)


def _add_keys_and_values(instance):
    Key = types.SimpleNamespace()
    default = instance.Default
    for name in (name for name in dir(default) if not name.startswith("_")):
        setattr(Key, name, name)
        setattr(instance, name, getattr(default, name))
    setattr(instance, "Key", Key)
    return instance


Gconf = _make_config()
Gopt = _make_options()
