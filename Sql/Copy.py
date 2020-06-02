#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.

COPY_CONFIG = """
INSERT OR REPLACE INTO main.config SELECT * FROM original.config
    WHERE key NOT IN ('Created', 'Updated', 'Opened', 'Worktime');
"""
COPY_MARKUP = """
INSERT OR REPLACE INTO main.markup SELECT * FROM original.markup;
"""
COPY_SPELLING = """
DELETE FROM main.spelling;
INSERT INTO main.spelling SELECT * FROM original.spelling;
"""
COPY_IGNORED_FIRSTS = """
DELETE FROM main.ignored_firsts;
INSERT INTO main.ignored_firsts SELECT * FROM original.ignored_firsts;
"""
COPY_AUTO_REPLACE = """
DELETE FROM main.auto_replace;
INSERT INTO main.auto_replace SELECT * FROM original.auto_replace;
"""
COPY_GROUPS = """
DELETE FROM main.grouped;
DELETE FROM main.groups;
INSERT OR REPLACE INTO main.groups SELECT * FROM original.groups;
"""

COPY_GROUPED = """
PRAGMA foreign_keys = 0;
INSERT INTO main.entries
    SELECT DISTINCT e.*
        FROM original.entries AS e, original.grouped AS g
        WHERE g.gid IN ({gids}) AND g.eid = e.eid;
DELETE FROM main.entries WHERE peid NOT IN (SELECT eid FROM main.entries);
PRAGMA foreign_keys = 1;
INSERT INTO main.xrefs
    SELECT DISTINCT x.*
        FROM original.xrefs AS x
        WHERE x.from_eid IN (SELECT eid FROM main.entries) AND
              x.to_eid IN (SELECT eid FROM main.entries);
INSERT INTO main.generic_xrefs
    SELECT DISTINCT x.*
        FROM original.generic_xrefs AS x
        WHERE x.from_eid IN (SELECT eid FROM main.entries);
INSERT INTO main.grouped
    SELECT DISTINCT g.*
        FROM original.grouped AS g
        WHERE g.eid IN (SELECT eid FROM main.entries);
INSERT INTO main.bookmarks
    SELECT DISTINCT b.*
        FROM original.bookmarks AS b
        WHERE b.eid IN (SELECT eid FROM main.entries);
"""
