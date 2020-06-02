#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

GET_VERSION = "PRAGMA user_version;"
SET_VERSION = "PRAGMA user_version = {};"


OPTIMIZE = """
BEGIN;
    DELETE FROM eid_map WHERE old_eid NOT IN (SELECT eid FROM entries);
    DELETE FROM eid_map WHERE new_eid NOT IN (SELECT eid FROM entries);
    DELETE FROM deleted_generic_xrefs WHERE from_eid NOT IN (
        SELECT eid FROM entries
        UNION
        SELECT eid FROM deleted_entries);
    DELETE FROM deleted_xrefs WHERE from_eid NOT IN (
       SELECT eid FROM entries
        UNION
        SELECT eid FROM deleted_entries);
    DELETE FROM deleted_xrefs WHERE to_eid NOT IN (
        SELECT eid FROM entries
        UNION
        SELECT eid FROM deleted_entries);
    DELETE FROM deleted_grouped
        WHERE gid NOT IN (SELECT gid FROM groups) OR eid NOT IN (
            SELECT eid FROM entries
            UNION
            SELECT eid FROM deleted_entries);
    UPDATE config SET value = 0 WHERE key = 'Opened';
    UPDATE config SET value = DATETIME('NOW') WHERE key = 'Updated';
COMMIT;
INSERT INTO term_words(term_words) VALUES('optimize');
INSERT INTO pages_words(pages_words) VALUES('optimize');
INSERT INTO note_words(note_words) VALUES('optimize');
VACUUM;
"""

# This must be done inside a transaction
CLOSE = """
UPDATE config SET value = DATETIME('NOW') WHERE key = 'Updated';
UPDATE config SET value = value + :seconds WHERE key = 'Worktime';
"""
