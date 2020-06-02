#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import enum
import uuid

import Lib
import Pages
import Spell
import Sql
from Config import Gconf, Gopt
from Const import (
    CountKind, FilterKind, IndentKind, LanguageKind, ROOT,
    SeeAlsoPositionKind, StyleKind, XrefKind, XRefToSubentryKind)


class Entry:

    def __init__(self, eid, saf, sortas, term, pages=None, notes=None, *,
                 peid=ROOT, indent=0, xrefCount=0, created=None,
                 updated=None):
        self.eid = eid
        self.saf = saf
        self.sortas = sortas
        self.term = term
        self.pages = pages
        self.notes = notes
        self.peid = peid
        self.indent = indent
        self.xrefCount = xrefCount
        self.created = created
        self.updated = updated


Xref = collections.namedtuple("Xref", "from_eid to_eid term kind")
DeletedEntry = collections.namedtuple(
    "DeletedEntry", "eid term pages peid")


def xref_for_data(data):            # data is, e.g., an Xix.Util.Xref in a
    data[-1] = XrefKind(data[-1])   # QComboBox item
    return Xref(*data)


def xref_for_record(record):
    return Xref(record[0], record[1], None, XrefKind(record[2]))


def generic_xref_for_record(eid, record):
    return Xref(eid, None, record[0], XrefKind(record[1]))


def to_basic_type(value):
    if isinstance(value, bool):
        return int(value)
    elif isinstance(value, enum.Enum):
        return value.value
    return value


def from_basic_type(key, value):
    if key in {"AltFontSize", "MonoFontSize", "Opened", "StdFontSize",
               "Worktime", "SectionPreLines", "SectionPostLines",
               "PadDigits", "HighestPageNumber", "LargestPageRange",
               "MostPages"}:
        return int(value)
    if key in {"MonoFontAsStrikeout", "SectionTitles", "IgnoreSubFirsts",
               "SuggestSpelled"}:
        return bool(int(value))
    if key in {"Indent", "IndentRTF"}:
        return IndentKind(int(value))
    if key == "Language":
        return LanguageKind(value)
    if key in {"SeeAlsoPosition", "SubSeeAlsoPosition"}:
        return SeeAlsoPositionKind(int(value))
    if key == "Style":
        return StyleKind(int(value))
    if key == "XRefToSubentry":
        return XRefToSubentryKind(int(value))
    return value


def create_xix(version, username, cursor, language, sortAsRules,
               pageRangeRules):
    cursor.execute(Sql.SET_VERSION.format(version))
    # Must be inside a transaction
    cursor.execute(Sql.CREATE_XIX, dict(
                   creator=username,
                   initials=Lib.initials(username),
                   stdfont=Gopt.StdFont,
                   stdfontsize=Gopt.StdFontSize,
                   altfont=Gopt.AltFont,
                   altfontsize=Gopt.AltFontSize,
                   monofont=Gopt.MonoFont,
                   monofontsize=Gopt.MonoFontSize,
                   xreftosubentry=Gconf.Default.XRefToSubentry,
                   see=Gconf.Default.See,
                   seeprefix=Gconf.Default.SeePrefix,
                   seesuffix=Gconf.Default.SeeSuffix,
                   seeseparator=Gconf.Default.SeeSeparator,
                   seealso=Gconf.Default.SeeAlso,
                   seealsoposition=Gconf.Default.SeeAlsoPosition,
                   seealsoprefix=Gconf.Default.SeeAlsoPrefix,
                   seealsosuffix=Gconf.Default.SeeAlsoSuffix,
                   seealsoseparator=Gconf.Default.SeeAlsoSeparator,
                   genericconjunction=Gconf.Default.GenericConjunction,
                   subsee=Gconf.Default.SubSee,
                   subseeprefix=Gconf.Default.SubSeePrefix,
                   subseesuffix=Gconf.Default.SubSeeSuffix,
                   subseeseparator=Gconf.Default.SubSeeSeparator,
                   subseealso=Gconf.Default.SubSeeAlso,
                   subseealsoposition=Gconf.Default.SubSeeAlsoPosition,
                   subseealsoprefix=Gconf.Default.SubSeeAlsoPrefix,
                   subseealsosuffix=Gconf.Default.SubSeeAlsoSuffix,
                   subseealsoseparator=Gconf.Default.SubSeeAlsoSeparator,
                   title=Gconf.Default.Title,
                   note=Gconf.Default.Note,
                   sectionprelines=Gconf.Default.SectionPreLines,
                   sectionpostlines=Gconf.Default.SectionPostLines,
                   sectiontitles=int(Gconf.Default.SectionTitles),
                   sectionspecialtitle=Gconf.Default.SectionSpecialTitle,
                   style=int(Gconf.Default.Style),
                   runinseparator=Gconf.Default.RunInSeparator,
                   paddigits=Gconf.Default.PadDigits,
                   ignoresubfirsts=Gconf.Default.IgnoreSubFirsts,
                   suggestspelled=Gconf.Default.SuggestSpelled,
                   highestpagenumber=Gconf.Default.HighestPageNumber,
                   largestpagerange=Gconf.Default.LargestPageRange,
                   mostpages=Gconf.Default.MostPages,
                   uuid=uuid.uuid4().hex.upper(),
                   ))
    assert language is not None
    cursor.executemany(Sql.INSERT_CONFIG, [
        dict(key=Gconf.Key.Creator, value=username),
        dict(key=Gconf.Key.Language, value=language.value),
        dict(key=Gconf.Key.SortAsRules, value=sortAsRules),
        dict(key=Gconf.Key.PageRangeRules, value=pageRangeRules),
        ])
    cursor.executemany(
        Sql.ADD_IGNORED_FIRSTS_WORD,
        [{"word": word} for word in Spell.Words.IGNORED_FIRSTS_WORDS])


def open_xix(user_version, version, username, cursor, db, pageRangeRules):
    if user_version < version:
        _update_database(db, cursor, version, user_version, username,
                         pageRangeRules)
    cursor.execute(
        "UPDATE config SET value = value + 1 WHERE key = 'Opened'")


def highestPage(pages):
    if not pages or not pages.strip():
        return 0
    i = pages.rfind(" ")
    page = pages if i == -1 else pages[i + 1:]
    if page.isdigit():
        return int(page)
    return 0


def register_functions(db):
    for name, function in ( # Caching is done in Python not SQLite
            ("searchablePages", Pages.searchablePages),
            ("hasOverlappingPages", Pages.hasOverlappingPages),
            ("largestPageRange", Pages.largestPageRange),
            ("pagesCount", Pages.pagesCount)):
        db.createscalarfunction(name, function, 1)
    db.createscalarfunction("htmlToCanonicalText", Lib.htmlToCanonicalText,
                            1, deterministic=True) # SQLite cache
    db.createscalarfunction("htmlToPlainText", Lib.htmlToPlainText, 1,
                            deterministic=True) # SQLite cache
    db.createscalarfunction("highestPage", highestPage, 1,
                            deterministic=True) # SQLite cache


def register_rules(db, *modules):
    for module in modules:
        for name in module.RulesForName:
            try:
                db.createscalarfunction( # APSW < 3.8.10.1
                    name, module.RulesForName[name].function,
                    deterministic=True)
            except TypeError:
                db.createscalarfunction( # APSW >= 3.8.10.1
                    name, module.RulesForName[name].function)


def sql_for_count(filter, eid=None):
    d = {}
    if filter in CountKind:
        sql = filter.sql_for_count()
        if filter is CountKind.SUBENTRIES:
            d = dict(peid=eid)
        elif filter is CountKind.XREFS:
            d = dict(eid=eid)
    else:
        sql = filter.sql_for_count()
    return sql, d


def sql_for_iterate(filter, match, offset, limit):
    d = dict(offset=offset, limit=limit)
    sql = filter.sql_for_iterate(match)
    if filter in {FilterKind.TERMS_MATCHING, FilterKind.NOTES_MATCHING,
                  FilterKind.IN_NORMAL_GROUP, FilterKind.IN_LINKED_GROUP,
                  FilterKind.ENTRIES_WITH_PAGES, FilterKind.TOO_HIGH_PAGE,
                  FilterKind.TOO_LARGE_PAGE_RANGE,
                  FilterKind.TOO_MANY_PAGES}:
        d["match"] = match
    return sql, d


def _update_database(db, cursor, xix_version, user_version, username,
                     pageRangeRules):
    # We have opened an .xix file that has an old format, so
    # use ALTER TABLE etc. to bring it up to date, and then
    # update its format.
    # Or copy if ALTER TABLE isn't sufficient
    # NOTE Any changes made here must be kept permanently for backward
    # compatibility
    cursor.execute(Sql.SET_VERSION.format(xix_version))
