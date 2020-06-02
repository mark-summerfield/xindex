#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.


INSERT_CONFIG = """
INSERT OR REPLACE INTO config (key, value) VALUES (:key, :value);"""
UPDATE_CONFIG = """
UPDATE OR REPLACE config SET value = :value WHERE key = :key;"""

INSERT_XREF = """
INSERT OR REPLACE INTO xrefs (from_eid, to_eid, kind) VALUES
    (:from_eid, :to_eid, :kind);
DELETE FROM deleted_xrefs WHERE from_eid = :from_eid AND to_eid = :to_eid;
"""
DELETE_XREF = """
INSERT INTO deleted_xrefs SELECT * FROM xrefs
    WHERE from_eid = :from_eid AND to_eid = :to_eid;
DELETE FROM xrefs
    WHERE from_eid = :from_eid AND to_eid = :to_eid;
"""
INSERT_GENERIC_XREF = """
INSERT OR REPLACE INTO generic_xrefs (from_eid, term, kind)
    VALUES (:from_eid, :term, :kind);
DELETE FROM deleted_generic_xrefs
    WHERE from_eid = :from_eid AND term = :term;
"""
DELETE_GENERIC_XREF = """
INSERT INTO deleted_generic_xrefs SELECT * FROM generic_xrefs
    WHERE from_eid = :from_eid AND term = :term;
DELETE FROM generic_xrefs
    WHERE from_eid = :from_eid AND term = :term;
"""

INSERT_ENTRY = """
INSERT INTO entries (saf, sortas, term, pages, notes, peid) VALUES
    (:saf, :sortas, :term, :pages, :notes, :peid);
SELECT LAST_INSERT_ROWID();
"""
REINSERT_ENTRY = """
INSERT INTO entries (eid, saf, sortas, term, pages, notes, peid)
    VALUES (:eid, :saf, :sortas, :term, :pages, :notes, :peid);
"""
REINSERT_ENTRY_WITH_DATES = """
INSERT INTO entries (eid, saf, sortas, term, pages, notes, peid,
                     created, updated)
VALUES (:eid, :saf, :sortas, :term, :pages, :notes, :peid,
        JULIANDAY(:created), JULIANDAY(:updated));
"""
UPDATE_ENTRY = """
UPDATE entries SET saf = :saf, sortas = :sortas,
    term = :term, pages = :pages, notes = :notes WHERE eid = :eid;
"""
REPARENT_ENTRY = "UPDATE entries SET peid = :peid WHERE eid = :eid;"
UNINSERT_ENTRY = """
DELETE FROM entries WHERE eid = :eid;
"""
DELETE_ENTRY = """
INSERT INTO deleted_entries SELECT * FROM entries WHERE entries.eid = :eid;
DELETE FROM entries WHERE eid = :eid;
"""
UNDELETE_ENTRY = """
INSERT INTO entries (eid, saf, sortas, term, pages, notes, peid)
    VALUES (:eid, :saf, :sortas, :term, :pages, :notes, :peid);
DELETE FROM deleted_entries WHERE eid = :eid;
"""
SYNC_PAGES = "UPDATE entries SET pages = :pages WHERE eid = :eid;"

DELETE_DELETED_ENTRY = """
DELETE FROM deleted_xrefs WHERE from_eid = :eid OR to_eid = :eid;
DELETE FROM deleted_generic_xrefs WHERE from_eid = :eid;
DELETE FROM deleted_grouped WHERE eid = :eid;
DELETE FROM deleted_entries WHERE eid = :eid;
"""

SET_EID_FOR_EID = """
INSERT OR REPLACE INTO eid_map (old_eid, new_eid)
    VALUES (:old_eid, :new_eid);
"""

ADD_SPELL_WORD = "INSERT OR IGNORE INTO spelling (word) VALUES (:word);"
REMOVE_SPELL_WORD = "DELETE FROM spelling WHERE word = :word;"

ADD_IGNORED_FIRSTS_WORD = """
INSERT OR IGNORE INTO ignored_firsts (word) VALUES (:word);"""
# For List Form
INSERT_IGNORED_FIRSTS_WORD = """
INSERT OR REPLACE INTO ignored_firsts (word) VALUES (?);"""
UPDATE_IGNORED_FIRSTS_WORD = """
UPDATE ignored_firsts SET word = ? WHERE word = ?;"""
DELETE_IGNORED_FIRSTS_WORD = "DELETE FROM ignored_firsts WHERE word = ?;"

EDIT_AUTO_REPLACE = """
INSERT OR REPLACE INTO auto_replace (word, replacement)
    VALUES (:word, :replacement);"""
DELETE_AUTO_REPLACE = "DELETE FROM auto_replace WHERE word = :word;"

UPDATE_PAGES = "UPDATE entries SET pages = :pages WHERE eid = :eid;"

SWAP_TERMS = """
UPDATE entries
    SET term = :term1, saf = :saf1, sortas = :sortas1 WHERE eid = :eid2;
UPDATE entries
    SET term = :term2, saf = :saf2, sortas = :sortas2 WHERE eid = :eid1;
"""

UPDATE_MARKUP = """
INSERT OR REPLACE INTO markup (
    extension, escapefunction, documentstart, documentend, note,
    sectionstart, sectionend, mainstart, mainend, sub1start, sub1end,
    sub2start, sub2end, sub3start, sub3end, sub4start, sub4end,
    sub5start, sub5end, sub6start, sub6end, sub7start, sub7end,
    sub8start, sub8end, sub9start, sub9end, encoding, rangeseparator,
    tab, newline, altfontstart, altfontend, monofontstart, monofontend,
    stdfontstart, stdfontend, boldstart, boldend, italicstart,
    italicend, subscriptend, subscriptstart, superscriptstart,
    superscriptend, underlinestart, underlineend, strikeoutstart,
    strikeoutend)
VALUES (
    :extension, :escapefunction, :documentstart, :documentend, :note,
    :sectionstart, :sectionend, :mainstart, :mainend, :sub1start,
    :sub1end, :sub2start, :sub2end, :sub3start, :sub3end, :sub4start,
    :sub4end, :sub5start, :sub5end, :sub6start, :sub6end, :sub7start,
    :sub7end, :sub8start, :sub8end, :sub9start, :sub9end, :encoding,
    :rangeseparator, :tab, :newline, :altfontstart, :altfontend,
    :monofontstart, :monofontend, :stdfontstart, :stdfontend,
    :boldstart, :boldend, :italicstart, :italicend, :subscriptend,
    :subscriptstart, :superscriptstart, :superscriptend,
    :underlinestart, :underlineend, :strikeoutstart, :strikeoutend);
"""

DELETE_MARKUP = "DELETE FROM markup WHERE extension = :extension;"

ADD_BOOKMARK = "INSERT OR IGNORE INTO bookmarks (eid) VALUES (:eid);"
REMOVE_BOOKMARK = "DELETE FROM bookmarks WHERE eid = :eid;"

# name is UNIQUE
ADD_GROUP = """
INSERT INTO groups (name, linked) VALUES (:name, :linked);
SELECT LAST_INSERT_ROWID();
"""
RE_ADD_GROUP = """
INSERT OR REPLACE INTO groups (gid, name, linked)
    VALUES (:gid, :name, :linked);"""
RENAME_GROUP = "UPDATE groups SET name = :name WHERE gid = :gid;"
DELETE_GROUP = """
DELETE FROM grouped WHERE gid = :gid;
DELETE FROM groups WHERE gid = :gid;
"""
UPDATE_GROUP = "UPDATE groups SET linked = :linked WHERE gid = :gid;"

ADD_TO_GROUP = """
INSERT OR IGNORE INTO grouped (gid, eid) VALUES (:gid, :eid);
DELETE FROM deleted_grouped WHERE gid = :gid AND eid = :eid;
"""
REMOVE_FROM_GROUP = """
INSERT OR IGNORE INTO deleted_grouped
    SELECT * FROM grouped WHERE gid = :gid AND eid = :eid;
DELETE FROM grouped WHERE gid = :gid AND eid = :eid;
"""
