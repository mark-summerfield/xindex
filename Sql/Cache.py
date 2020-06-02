#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.


CREATE_XIX_CACHES = """
DROP TABLE IF EXISTS entries_cache;

CREATE TEMP TABLE entries_cache (
    cid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    indent INTEGER DEFAULT 0 NOT NULL,
    eid INTEGER
);
"""
for name in ("overlapping_pages_cache", "same_term_texts_cache"):
    CREATE_XIX_CACHES += """
DROP TABLE IF EXISTS {0};

CREATE TEMP TABLE {0} (
    cid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    eid INTEGER
);
""".format(name)

ENTRIES_CACHE_REFRESH = """
DELETE FROM entries_cache;
INSERT INTO entries_cache (indent, eid)
    WITH RECURSIVE
        tree(eid, indent, sortas) AS (
            VALUES(0, -1, '')
            UNION ALL
            SELECT entries.eid, tree.indent + 1 AS depth, entries.sortas
                FROM entries JOIN tree ON entries.peid = tree.eid
                ORDER BY depth DESC, entries.sortas
        )
        SELECT indent, eid FROM tree;
"""
ENTRIES_CACHE_COUNT = "SELECT COUNT(*) FROM entries_cache;"

HAS_OVERLAPPING_PAGES_CACHE_REFRESH = """
DELETE FROM overlapping_pages_cache;
INSERT INTO overlapping_pages_cache (eid)
    SELECT eid FROM entries WHERE hasOverlappingPages(pages)
    ORDER BY sortas, peid;
"""
HAS_OVERLAPPING_PAGES_CACHE_COUNT = """
SELECT COUNT(*) FROM overlapping_pages_cache;"""

SAME_TERM_TEXTS_CACHE_REFRESH = """
DELETE FROM same_term_texts_cache;
INSERT INTO same_term_texts_cache (eid)
    SELECT entries1.eid FROM entries AS entries1, entries AS entries2
        WHERE entries1.eid != 0 AND entries2.eid != 0
        AND entries1.eid != entries2.eid
        AND entries1.peid = entries2.peid
        AND htmlToCanonicalText(entries1.term) =
            htmlToCanonicalText(entries2.term)
    ORDER BY entries1.sortas, entries1.peid;
"""
SAME_TERM_TEXTS_CACHE_COUNT = """
SELECT COUNT(*) FROM same_term_texts_cache;"""

CACHES_CLEAR = """
DELETE FROM entries_cache;
DELETE FROM overlapping_pages_cache;
DELETE FROM same_term_texts_cache;
"""
