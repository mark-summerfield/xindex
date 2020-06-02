#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import enum
import re

import roman

import Sql


PAGE_ORDER_RX = re.compile(
    r"^[RD](?P<start>[\dCDILMVX]+)TO(?P<end>[\dCDILMVX]+)$")


class ModeKind(enum.Enum):
    VIEW = "Viewing"
    EDIT = "Editing"
    ADD = "Adding"
    CHANGE = "Changing"
    NO_INDEX = "No Index"


@enum.unique
class CountKind(enum.IntEnum):
    ENTRIES = 1
    TOP_LEVEL_ENTRIES = 2
    SUBENTRIES = 3
    DELETED_ENTRIES = 4
    XREFS = 5
    def sql_for_count(self):
        return getattr(Sql, "COUNT_" + self.name.upper())


class CommandKind(enum.Enum):
    DO = 1
    UNDO = 2


class LanguageKind(enum.Enum):
    AMERICAN = "American"
    AUSTRALIAN = "Australian"
    BRITISH = "British"
    CANADIAN = "Canadian"
    SOUTH_AFRICAN = "South African"


@enum.unique
class IndentKind(enum.IntEnum):
    TAB = 0
    ONE_SPACE = 1
    TWO_SPACES = 2
    THREE_SPACES = 3
    FOUR_SPACES = 4


@enum.unique
class XrefKind(enum.IntEnum):
    SEE = 1
    SEE_ALSO = 2
    SEE_GENERIC = 3
    SEE_ALSO_GENERIC = 4


@enum.unique
class SeeAlsoPositionKind(enum.IntEnum):
    AFTER_PAGES = 1
    FIRST_SUBENTRY = 2
    LAST_SUBENTRY = 3
    @property
    def text(self):
        if self is SeeAlsoPositionKind.AFTER_PAGES:
            return "After Pages"
        elif self is SeeAlsoPositionKind.FIRST_SUBENTRY:
            return "As First Subentry"
        elif self is SeeAlsoPositionKind.LAST_SUBENTRY:
            return "As Last Subentry"


@enum.unique
class XRefToSubentryKind(enum.IntEnum):
    COLON = 0
    COMMA = 1
    UNDER = 2
    @property
    def text(self):
        if self is XRefToSubentryKind.COLON:
            return "main term: subterm"
        elif self is XRefToSubentryKind.COMMA:
            return "main term, subterm"
        if self is XRefToSubentryKind.UNDER:
            return "under main term"


@enum.unique
class StyleKind(enum.IntEnum):
    INDENTED = -1
    RUN_IN_FROM_MAIN = 0
    RUN_IN_FROM_SUBENTRY1 = 1
    RUN_IN_FROM_SUBENTRY2 = 2
    RUN_IN_FROM_SUBENTRY3 = 3
    RUN_IN_FROM_SUBENTRY4 = 4
    RUN_IN_FROM_SUBENTRY5 = 5
    @property
    def text(self):
        if self is StyleKind.INDENTED:
            return "Indented"
        elif self is StyleKind.RUN_IN_FROM_MAIN:
            return "Run-in from Main Entries"
        elif self is StyleKind.RUN_IN_FROM_SUBENTRY1:
            return "Run-in from 1st Subentries"
        elif self is StyleKind.RUN_IN_FROM_SUBENTRY2:
            return "Run-in from 2nd Subentries"
        elif self is StyleKind.RUN_IN_FROM_SUBENTRY3:
            return "Run-in from 3rd Subentries"
        elif self is StyleKind.RUN_IN_FROM_SUBENTRY4:
            return "Run-in from 4th Subentries"
        elif self is StyleKind.RUN_IN_FROM_SUBENTRY5:
            return "Run-in from 5th Subentries"


class FileKind(enum.Enum):
    RTF = 0
    DOCX = 1
    TXT = 2
    HTML = 3
    IXML = 4
    PDF = 5
    PRINT = 6
    USER = 7


@enum.unique
class PaperSizeKind(enum.IntEnum):
    LETTER = 0
    A4 = 4


class EntryDataKind(enum.Enum):
    EID = 1
    INDENT_AND_EID = 2
    ALL_DATA = 3
    ALL_DATA_AND_XREF = 4
    ALL_DATA_AND_DATES = 5


class SearchFieldKind(enum.Enum):
    TERM = 1
    PAGES = 2
    NOTES = 3


@enum.unique
class PartKind(enum.IntEnum):
    TAG = 0
    TEXT = 1


@enum.unique
class CandidateKind(enum.IntEnum):
    PHRASE = 1
    ROMAN = 2
    NUMBER = 3
    LITERAL = 4
    UNCHANGED = 5


@enum.unique # Must match Sql/PageOrder.py PAGE_ORDERS
class PagesOrderKind(enum.IntEnum):
    RITOXLIX = 1
    RLTOC = 2
    D1TO49 = 3
    D50TO99 = 4
    D100TO149 = 5
    D150TO199 = 6
    D200TO249 = 7
    D250TO299 = 8
    D300TO349 = 9
    D350TO399 = 10
    D400TO449 = 11
    D450TO499 = 12
    D500TO599 = 13
    D600TO699 = 14
    D700TO799 = 15
    D800TO899 = 16
    D900TO999 = 17
    D1000TO1199 = 18
    D1200TO1399 = 19
    D1400TO1599 = 20
    D1600TO1799 = 21
    D1800TO2000 = 22
    @property
    def text(self):
        match = PAGE_ORDER_RX.match(self.name)
        if match is not None:
            return "Pages {}-{}".format(match.group("start"),
                                        match.group("end"))
    @property
    def start_end(self):
        match = PAGE_ORDER_RX.match(self.name)
        if match is not None:
            start = match.group("start")
            end = match.group("end")
            if start.isdigit():
                return int(start), int(end)
            start = roman.fromRoman(start)
            end = roman.fromRoman(end)
            return start, end


@enum.unique
class FilterKind(enum.IntEnum):
    TERMS_MATCHING = 0
    ENTRIES_WITH_PAGES = 1
    NOTES_MATCHING = 2
    IN_NORMAL_GROUP = 3
    IN_LINKED_GROUP = 4
    CREATION_ORDER = 5
    UPDATED_ORDER = 6
    PAGES_ORDER = 7
    NO_PAGES_NO_SUBENTRIES_NO_XREFS = 8
    NO_PAGES_AND_NO_SUBENTRIES = 9
    PAGES_AND_SEE_XREF = 10
    HAS_NO_SUBENTRIES = 11
    HAS_ONE_SUBENTRY = 12
    HAS_TWO_SUBENTRIES = 13
    HAS_SUBENTRIES = 14
    HAS_SEE_OR_SEE_ALSO = 15
    HAS_GENERIC_SEE_OR_SEE_ALSO = 16
    HAS_NOTES = 17
    NO_AUTOMATIC_SORT_AS = 18
    HAS_OVERLAPPING_PAGES = 19
    TOO_HIGH_PAGE = 20
    TOO_LARGE_PAGE_RANGE = 21
    TOO_MANY_PAGES = 22
    SAME_TERM_TEXTS = 23
    FIRST_SUBENTRIES = 24
    SECOND_SUBENTRIES = 25
    THIRD_SUBENTRIES = 26
    FOURTH_SUBENTRIES = 27
    FIFTH_SUBENTRIES = 28
    @property
    def text(self):
        if self is FilterKind.TERMS_MATCHING:
            return "Terms Matching:"
        elif self is FilterKind.ENTRIES_WITH_PAGES:
            return "Pages Matching:"
        elif self is FilterKind.NOTES_MATCHING:
            return "Notes Matching:"
        elif self is FilterKind.IN_NORMAL_GROUP:
            return "Normal Group:"
        elif self is FilterKind.IN_LINKED_GROUP:
            return "Linked Group:"
        elif self is FilterKind.CREATION_ORDER:
            return "In Created Order (Newest First)"
        elif self is FilterKind.UPDATED_ORDER:
            return "In Edited Order (Most Recent First)"
        elif self is FilterKind.PAGES_ORDER:
            return "In Page Number Order"
        elif self is FilterKind.NO_PAGES_NO_SUBENTRIES_NO_XREFS:
            return "No Pages, Subentries, or Cross-references"
        elif self is FilterKind.NO_PAGES_AND_NO_SUBENTRIES:
            return "No Pages or Subentries"
        elif self is FilterKind.PAGES_AND_SEE_XREF:
            return "Pages and See cross-reference(s)"
        elif self is FilterKind.HAS_NO_SUBENTRIES:
            return "No Subentries"
        elif self is FilterKind.HAS_ONE_SUBENTRY:
            return "Has One Subentry"
        elif self is FilterKind.HAS_TWO_SUBENTRIES:
            return "Has Two Subentries"
        elif self is FilterKind.HAS_SUBENTRIES:
            return "Has Subentries"
        elif self is FilterKind.HAS_SEE_OR_SEE_ALSO:
            return "Has Cross-references"
        elif self is FilterKind.HAS_GENERIC_SEE_OR_SEE_ALSO:
            return "Has Generic Cross-references"
        elif self is FilterKind.HAS_NOTES:
            return "Has Notes"
        elif self is FilterKind.NO_AUTOMATIC_SORT_AS:
            return "Has Custom Sort As"
        elif self is FilterKind.HAS_OVERLAPPING_PAGES:
            return "Overlapping Pages"
        elif self is FilterKind.TOO_HIGH_PAGE:
            return "Too High Page Number"
        elif self is FilterKind.TOO_LARGE_PAGE_RANGE:
            return "Too Large Page Range"
        elif self is FilterKind.TOO_MANY_PAGES:
            return "Too Many Pages"
        elif self is FilterKind.SAME_TERM_TEXTS:
            return "Same Term Texts"
        elif self is FilterKind.FIRST_SUBENTRIES:
            return "First Subentries"
        elif self is FilterKind.SECOND_SUBENTRIES:
            return "Second Subentries"
        elif self is FilterKind.THIRD_SUBENTRIES:
            return "Third Subentries"
        elif self is FilterKind.FOURTH_SUBENTRIES:
            return "Fourth Subentries"
        elif self is FilterKind.FIFTH_SUBENTRIES:
            return "Fifth Subentries"
    def sql_for_count(self, pageOrder=None):
        if self is FilterKind.PAGES_ORDER:
            pageOrder = PagesOrderKind(pageOrder)
            key = "PAGES_ORDER_{}_COUNT".format(pageOrder.name.upper())
        else:
            key = "{}_COUNT".format(self.name.upper())
        return getattr(Sql, key)
    def sql_for_iterate(self, pageOrder=None):
        if self is FilterKind.PAGES_ORDER:
            pageOrder = PagesOrderKind(pageOrder)
            key = "PAGES_ORDER_{}_EIDS".format(pageOrder.name.upper())
        else:
            key = "{}_EIDS".format(self.name.upper())
        return getattr(Sql, key)
    @property
    def isCheck(self):
        if self in {FilterKind.SAME_TERM_TEXTS,
                    FilterKind.HAS_OVERLAPPING_PAGES,
                    FilterKind.TOO_HIGH_PAGE,
                    FilterKind.TOO_LARGE_PAGE_RANGE,
                    FilterKind.TOO_MANY_PAGES}:
            return True
        return False
