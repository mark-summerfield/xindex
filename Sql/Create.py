#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.


PREPARE_XIX = """
PRAGMA foreign_keys = 1;
PRAGMA temp_store = MEMORY;
PRAGMA encoding = "UTF-8";
"""

CREATE_XIX = """
DROP TRIGGER IF EXISTS insert_entry_trigger;
DROP TRIGGER IF EXISTS update_entry_trigger;
DROP TRIGGER IF EXISTS update_entry_term_trigger;
DROP TRIGGER IF EXISTS update_entry_notes_trigger;
DROP TRIGGER IF EXISTS update_entry_pages_trigger;
DROP TRIGGER IF EXISTS delete_entry_trigger;
DROP INDEX IF EXISTS i_entries_peid;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS term_words;
DROP TABLE IF EXISTS note_words;
DROP TABLE IF EXISTS pages_words;
DROP TABLE IF EXISTS deleted_entries;
DROP TABLE IF EXISTS xrefs;
DROP TABLE IF EXISTS deleted_xrefs;
DROP TABLE IF EXISTS generic_xrefs;
DROP TABLE IF EXISTS deleted_generic_xrefs;
DROP TABLE IF EXISTS eid_map;
DROP TABLE IF EXISTS spelling;
DROP TABLE IF EXISTS ignored_firsts;
DROP TABLE IF EXISTS auto_replace;
DROP TABLE IF EXISTS config;
DROP TABLE IF EXISTS markup;
DROP TABLE IF EXISTS bookmarks;
DROP TABLE IF EXISTS groups;
DROP TABLE IF EXISTS grouped;
DROP TABLE IF EXISTS deleted_grouped;


CREATE TABLE entries (
    eid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    peid INTEGER, -- NULL only allowed for ROOT

    saf TEXT DEFAULT 'A' NOT NULL, -- flags
    sortas TEXT NOT NULL, -- sort as - plain text
    term TEXT NOT NULL, -- display - html text
    pages TEXT, -- page references - html text
    notes TEXT, -- notes - html text
    created REAL DEFAULT (JULIANDAY('NOW')) NOT NULL,
    updated REAL DEFAULT (JULIANDAY('NOW')) NOT NULL,

    FOREIGN KEY(peid) REFERENCES entries(eid),
    CHECK(CASE WHEN peid IS NULL AND eid != 0 THEN 0 END),
    CHECK(eid != peid)
);

CREATE INDEX i_entries_peid ON entries(peid);

CREATE VIRTUAL TABLE term_words USING FTS4();

CREATE VIRTUAL TABLE note_words USING FTS4();

CREATE VIRTUAL TABLE pages_words USING FTS4();

CREATE TRIGGER insert_entry_trigger AFTER INSERT ON entries
    FOR EACH ROW
    BEGIN
        INSERT OR REPLACE INTO term_words (docid, content) VALUES
            (NEW.eid, htmlToPlainText(NEW.term));
        INSERT OR REPLACE INTO note_words (docid, content) VALUES
            (NEW.eid, htmlToPlainText(NEW.notes));
        INSERT OR REPLACE INTO pages_words (docid, content) VALUES
            (NEW.eid, searchablePages(NEW.pages));
    END;

CREATE TRIGGER update_entry_trigger AFTER UPDATE ON entries
    FOR EACH ROW
    BEGIN
        UPDATE entries SET updated = JULIANDAY('NOW') WHERE eid = OLD.eid;
    END;

CREATE TRIGGER update_entry_term_trigger AFTER UPDATE OF term ON entries
    FOR EACH ROW
    BEGIN
        INSERT OR REPLACE INTO term_words (docid, content) VALUES
            (NEW.eid, htmlToPlainText(NEW.term));
    END;

CREATE TRIGGER update_entry_notes_trigger AFTER UPDATE OF notes ON entries
    FOR EACH ROW
    BEGIN
        INSERT OR REPLACE INTO note_words (docid, content) VALUES
            (NEW.eid, htmlToPlainText(NEW.notes));
    END;

CREATE TRIGGER update_entry_pages_trigger AFTER UPDATE OF pages ON entries
    FOR EACH ROW
    BEGIN
        INSERT OR REPLACE INTO pages_words (docid, content) VALUES
            (NEW.eid, searchablePages(NEW.pages));
    END;

CREATE TRIGGER delete_entry_trigger AFTER DELETE ON entries
    FOR EACH ROW
    BEGIN
        DELETE FROM term_words WHERE docid = OLD.eid;
        DELETE FROM note_words WHERE docid = OLD.eid;
        DELETE FROM pages_words WHERE docid = OLD.eid;
    END;

CREATE TABLE deleted_entries (
    eid INTEGER PRIMARY KEY NOT NULL,
    peid INTEGER NOT NULL,

    saf TEXT DEFAULT 'A' NOT NULL, -- flags
    sortas TEXT NOT NULL, -- sort as - plain text
    term TEXT NOT NULL, -- display - html text
    pages TEXT, -- page references - html text
    notes TEXT, -- notes - html text
    created REAL DEFAULT (JULIANDAY('NOW')) NOT NULL,
    updated REAL DEFAULT (JULIANDAY('NOW')) NOT NULL
);

CREATE TABLE xrefs (
    from_eid INTEGER NOT NULL,
    to_eid INTEGER NOT NULL,
    kind INTEGER NOT NULL DEFAULT 1, -- 1 see;  2 see also

    PRIMARY KEY(from_eid, to_eid),
    FOREIGN KEY(from_eid) REFERENCES entries(eid),
    FOREIGN KEY(to_eid) REFERENCES entries(eid),
    CHECK(kind IN (1, 2) AND from_eid != to_eid)
);

CREATE TABLE deleted_xrefs (
    from_eid INTEGER NOT NULL,
    to_eid INTEGER NOT NULL,
    kind INTEGER NOT NULL DEFAULT 1, -- 1 see;  2 see also

    PRIMARY KEY(from_eid, to_eid),
    CHECK(kind IN (1, 2))
);

CREATE TABLE generic_xrefs (
    from_eid INTEGER NOT NULL,
    term TEXT NOT NULL, -- html text
    kind INTEGER NOT NULL DEFAULT 3, -- 3 see;  4 see also

    PRIMARY KEY(from_eid, term),
    FOREIGN KEY(from_eid) REFERENCES entries(eid),
    CHECK(kind IN (3, 4))
);

CREATE TABLE deleted_generic_xrefs (
    from_eid INTEGER NOT NULL,
    term TEXT NOT NULL, -- html text
    kind INTEGER NOT NULL DEFAULT 3, -- 3 see;  4 see also

    PRIMARY KEY(from_eid, term),
    CHECK(kind IN (3, 4))
);

CREATE TABLE eid_map (
    old_eid INTEGER PRIMARY KEY NOT NULL,
    new_eid INTEGER NOT NULL
);

CREATE TABLE spelling (
    word TEXT PRIMARY KEY UNIQUE NOT NULL
) WITHOUT ROWID;

CREATE TABLE ignored_firsts (
    word TEXT PRIMARY KEY UNIQUE NOT NULL
) WITHOUT ROWID;

CREATE TABLE auto_replace (
    word TEXT PRIMARY KEY NOT NULL,
    replacement TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE config (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT
) WITHOUT ROWID;

CREATE TABLE markup (
    extension TEXT PRIMARY KEY NOT NULL,
    escapefunction TEXT DEFAULT '' NOT NULL,
    documentstart TEXT DEFAULT '' NOT NULL,
    documentend TEXT DEFAULT '' NOT NULL,
    note TEXT DEFAULT '' NOT NULL,
    sectionstart TEXT DEFAULT '' NOT NULL,
    sectionend TEXT DEFAULT '' NOT NULL,
    mainstart TEXT DEFAULT '' NOT NULL,
    mainend TEXT DEFAULT '' NOT NULL,
    sub1start TEXT DEFAULT '' NOT NULL,
    sub1end TEXT DEFAULT '' NOT NULL,
    sub2start TEXT DEFAULT '' NOT NULL,
    sub2end TEXT DEFAULT '' NOT NULL,
    sub3start TEXT DEFAULT '' NOT NULL,
    sub3end TEXT DEFAULT '' NOT NULL,
    sub4start TEXT DEFAULT '' NOT NULL,
    sub4end TEXT DEFAULT '' NOT NULL,
    sub5start TEXT DEFAULT '' NOT NULL,
    sub5end TEXT DEFAULT '' NOT NULL,
    sub6start TEXT DEFAULT '' NOT NULL,
    sub6end TEXT DEFAULT '' NOT NULL,
    sub7start TEXT DEFAULT '' NOT NULL,
    sub7end TEXT DEFAULT '' NOT NULL,
    sub8start TEXT DEFAULT '' NOT NULL,
    sub8end TEXT DEFAULT '' NOT NULL,
    sub9start TEXT DEFAULT '' NOT NULL,
    sub9end TEXT DEFAULT '' NOT NULL,
    encoding TEXT DEFAULT 'UTF-8' NOT NULL,
    rangeseparator TEXT DEFAULT '\u2013' NOT NULL,
    tab TEXT DEFAULT '\t' NOT NULL,
    newline TEXT DEFAULT '\n' NOT NULL,
    altfontstart TEXT DEFAULT '' NOT NULL,
    altfontend TEXT DEFAULT '' NOT NULL,
    monofontstart TEXT DEFAULT '' NOT NULL,
    monofontend TEXT DEFAULT '' NOT NULL,
    stdfontstart TEXT DEFAULT '' NOT NULL,
    stdfontend TEXT DEFAULT '' NOT NULL,
    boldstart TEXT DEFAULT '' NOT NULL,
    boldend TEXT DEFAULT '' NOT NULL,
    italicstart TEXT DEFAULT '' NOT NULL,
    italicend TEXT DEFAULT '' NOT NULL,
    subscriptend TEXT DEFAULT '' NOT NULL,
    subscriptstart TEXT DEFAULT '' NOT NULL,
    superscriptstart TEXT DEFAULT '' NOT NULL,
    superscriptend TEXT DEFAULT '' NOT NULL,
    underlinestart TEXT DEFAULT '' NOT NULL,
    underlineend TEXT DEFAULT '' NOT NULL,
    strikeoutstart TEXT DEFAULT '' NOT NULL,
    strikeoutend TEXT DEFAULT '' NOT NULL
) WITHOUT ROWID;

CREATE TABLE bookmarks (
    eid INTEGER PRIMARY KEY NOT NULL,

    FOREIGN KEY(eid) REFERENCES entries(eid)
);

CREATE TABLE groups (
    gid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT UNIQUE NOT NULL,
    linked INTEGER NOT NULL DEFAULT 0,

    CHECK(linked IN (0, 1))
);

CREATE TABLE grouped (
    gid INTEGER NOT NULL,
    eid INTEGER NOT NULL,

    PRIMARY KEY(gid, eid),
    FOREIGN KEY(gid) REFERENCES groups(gid),
    FOREIGN KEY(eid) REFERENCES entries(eid)
);

CREATE TABLE deleted_grouped (
    gid INTEGER NOT NULL,
    eid INTEGER NOT NULL,

    PRIMARY KEY(gid, eid)
);

INSERT INTO entries (eid, sortas, term) VALUES (0, '', ''); -- ROOT

INSERT INTO markup (
    extension, escapefunction, sectionstart, sectionend, mainstart, mainend,
    sub1start, sub1end, sub2start, sub2end, sub3start, sub3end, sub4start,
    sub4end, sub5start, sub5end, sub6start, sub6end, sub7start, sub7end,
    sub8start, sub8end, sub9start, sub9end, rangeseparator, boldstart,
    boldend, italicstart, italicend, subscriptstart, subscriptend,
    superscriptstart, superscriptend)
VALUES ('.ucp', 'ucp', '', '{nl}', '    <p>', '</p>{nl}', '<h1>',
        '</>{nl}', '<h2>', '</>{nl}', '<h3>', '</>{nl}', '<h4>',
        '</>{nl}', '<h5>', '</>{nl}', '<h6>', '</>', '<h7>', '</>{nl}',
        '<h8>', '</>{nl}', '<h9>', '</>{nl}', '<#8211>', '<e1>',
        '</e1>', '<i>', '</i>', '<sub>', '</sub>', '<sup>', '</sup>');

INSERT INTO config (key, value) VALUES ('Created', DATETIME('NOW'));
INSERT INTO config (key, value) VALUES ('Updated', DATETIME('NOW'));
INSERT INTO config (key, value) VALUES ('Opened', 1);
INSERT INTO config (key, value) VALUES ('Worktime', 0);
INSERT INTO config (key, value) VALUES ('Creator', :creator);
INSERT INTO config (key, value) VALUES ('Initials', :initials);
INSERT INTO config (key, value) VALUES ('Indent', 0);
INSERT INTO config (key, value) VALUES ('TermPagesSeparator', ', ');
INSERT INTO config (key, value) VALUES ('StdFont', :stdfont);
INSERT INTO config (key, value) VALUES ('StdFontSize', :stdfontsize);
INSERT INTO config (key, value) VALUES ('AltFont', :altfont);
INSERT INTO config (key, value) VALUES ('AltFontSize', :altfontsize);
INSERT INTO config (key, value) VALUES ('MonoFont', :monofont);
INSERT INTO config (key, value) VALUES ('MonoFontSize', :monofontsize);
INSERT INTO config (key, value) VALUES ('MonoFontAsStrikeout', 0);
INSERT INTO config (key, value) VALUES ('XRefToSubentry', :xreftosubentry);
INSERT INTO config (key, value) VALUES ('See', :see);
INSERT INTO config (key, value) VALUES ('SeePrefix', :seeprefix);
INSERT INTO config (key, value) VALUES ('SeeSuffix', :seesuffix);
INSERT INTO config (key, value) VALUES ('SeeSeparator', :seeseparator);
INSERT INTO config (key, value) VALUES ('SeeAlso', :seealso);
INSERT INTO config (key, value) VALUES ('SeeAlsoPosition',
    :seealsoposition);
INSERT INTO config (key, value) VALUES ('SeeAlsoPrefix', :seealsoprefix);
INSERT INTO config (key, value) VALUES ('SeeAlsoSuffix', :seealsosuffix);
INSERT INTO config (key, value) VALUES ('SeeAlsoSeparator',
    :seealsoseparator);
INSERT INTO config (key, value) VALUES ('GenericConjunction',
    :genericconjunction);
INSERT INTO config (key, value) VALUES ('SubSee', :subsee);
INSERT INTO config (key, value) VALUES ('SubSeePrefix', :subseeprefix);
INSERT INTO config (key, value) VALUES ('SubSeeSuffix', :subseesuffix);
INSERT INTO config (key, value) VALUES ('SubSeeSeparator',
    :subseeseparator);
INSERT INTO config (key, value) VALUES ('SubSeeAlso', :subseealso);
INSERT INTO config (key, value) VALUES ('SubSeeAlsoPosition',
    :subseealsoposition);
INSERT INTO config (key, value) VALUES ('SubSeeAlsoPrefix',
    :subseealsoprefix);
INSERT INTO config (key, value) VALUES ('SubSeeAlsoSuffix',
    :subseealsosuffix);
INSERT INTO config (key, value) VALUES ('SubSeeAlsoSeparator',
    :subseealsoseparator);
INSERT INTO config (key, value) VALUES ('Title', :title);
INSERT INTO config (key, value) VALUES ('Note', :note);
INSERT INTO config (key, value) VALUES ('Style', :style);
INSERT INTO config (key, value) VALUES ('RunInSeparator', :runinseparator);
INSERT INTO config (key, value) VALUES ('SectionPreLines',
    :sectionprelines);
INSERT INTO config (key, value) VALUES ('SectionPostLines',
    :sectionpostlines);
INSERT INTO config (key, value) VALUES ('SectionTitles', :sectiontitles);
INSERT INTO config (key, value) VALUES ('SectionSpecialTitle',
    :sectionspecialtitle);
INSERT INTO config (key, value) VALUES ('PadDigits', :paddigits);
INSERT INTO config (key, value) VALUES ('IgnoreSubFirsts',
    :ignoresubfirsts);
INSERT INTO config (key, value) VALUES ('SuggestSpelled',
    :suggestspelled);
INSERT INTO config (key, value) VALUES ('HighestPageNumber',
    :highestpagenumber);
INSERT INTO config (key, value) VALUES ('LargestPageRange',
    :largestpagerange);
INSERT INTO config (key, value) VALUES ('MostPages',
    :mostpages);
INSERT INTO config (key, value) VALUES ('UUID', :uuid);
"""
