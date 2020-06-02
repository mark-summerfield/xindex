#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.


GET_CONFIG_VALUE = "SELECT value FROM config WHERE key = :key;"
CONFIGS = "SELECT key, value FROM config;"

XREF_OPTIONS = "SELECT key, value FROM config WHERE key LIKE 'See%';"

COUNT_ENTRIES = "SELECT COUNT(*) - 1 FROM entries;" # Allow for ROOT
COUNT_TOP_LEVEL_ENTRIES = "SELECT COUNT(*) FROM entries WHERE peid = 0;"
COUNT_SUBENTRIES = "SELECT COUNT(*) FROM entries WHERE peid = :peid;"
COUNT_XREFS = """
SELECT
    (SELECT COUNT(*) FROM xrefs WHERE from_eid = :eid OR to_eid = :eid)
    +
    (SELECT COUNT(*) FROM generic_xrefs WHERE from_eid = :eid)
AS total;"""
COUNT_DELETED_ENTRIES = "SELECT COUNT(*) FROM deleted_entries;"

XREF_COUNT = """
SELECT
    (SELECT COUNT(*) FROM xrefs WHERE from_eid = :eid)
    +
    (SELECT COUNT(*) FROM generic_xrefs WHERE from_eid = :eid)
AS total;
"""

HAS_DELETED_ENTRY = """
SELECT EXISTS (SELECT 1 FROM deleted_entries WHERE eid = :eid LIMIT 1);
"""
GET_DELETED_ENTRY = """
SELECT eid, saf, sortas, term, pages, notes, peid
FROM deleted_entries WHERE eid = :eid LIMIT 1;
"""
HAS_ENTRY = """
SELECT EXISTS (SELECT 1 FROM entries WHERE eid = :eid LIMIT 1);
"""
GET_ENTRY = """
SELECT eid, saf, sortas, term, pages, notes, peid FROM entries
WHERE eid = :eid LIMIT 1;
"""
GET_ENTRY_AND_DATES = """
SELECT eid, saf, sortas, term, pages, notes, peid,
    DATETIME(created), DATETIME(updated)
FROM entries WHERE eid = :eid LIMIT 1;
"""
GET_TERM = """
SELECT term FROM entries WHERE eid = :eid LIMIT 1;
"""
GET_PEID = "SELECT peid FROM entries WHERE eid = :eid LIMIT 1;"
GET_XREFS = """
SELECT to_eid, kind FROM xrefs, entries
    WHERE from_eid = :eid AND to_eid = entries.eid
    ORDER BY kind, LOWER(entries.term);
"""
GET_ALL_XREFS = """
SELECT from_eid, to_eid, term, kind FROM (
    SELECT from_eid, to_eid, '' AS term, kind FROM xrefs
        WHERE from_eid = :eid OR to_eid = :eid
    UNION
    SELECT from_eid, NULL AS to_eid, term, kind FROM generic_xrefs
        WHERE from_eid = :eid
);
"""
HAS_SUBENTRY = """
SELECT EXISTS (SELECT 1 FROM entries WHERE peid = :eid LIMIT 1);
"""
GET_GENERIC_XREFS = """
SELECT term, kind FROM generic_xrefs WHERE from_eid = :eid
    ORDER BY LOWER(term);"""

DELETED_ENTRIES = """
SELECT eid, term, pages, peid FROM deleted_entries ORDER BY peid, sortas;
"""
DELETED_SUBENTRIES = "SELECT eid FROM deleted_entries WHERE peid = :eid;"

DELETED_XREFS = """
SELECT from_eid, to_eid, kind FROM deleted_xrefs
    WHERE from_eid = :eid OR to_eid = :eid;
"""
DELETABLE_XREFS = """
SELECT from_eid, to_eid, kind FROM xrefs
    WHERE from_eid = :eid OR to_eid = :eid;
"""
DELETED_GENERIC_XREFS = """
SELECT term, kind FROM deleted_generic_xrefs WHERE from_eid = :eid;
"""
DELETABLE_GENERIC_XREFS = """
SELECT term, kind FROM generic_xrefs WHERE from_eid = :eid;
"""
# Returns the EIDs (including this one) in bottom up order for safe
# deletion
DELETABLE_EIDS = """
WITH RECURSIVE
    tree(eid, indent) AS (
        VALUES(:peid, -1)
        UNION ALL
        SELECT entries.eid, tree.indent + 1
            FROM entries JOIN tree ON entries.peid = tree.eid
    )
    SELECT eid FROM tree ORDER BY indent DESC, eid;
"""

GET_EID_FOR_EID = "SELECT new_eid FROM eid_map WHERE old_eid = :eid;"

GET_SPELL_WORDS = "SELECT word FROM spelling;"

GET_IGNORED_FIRSTS_WORDS = "SELECT word FROM ignored_firsts;"
# For ListForm
SORTED_IGNORED_FIRSTS_WORDS = """
SELECT word FROM ignored_firsts ORDER BY LOWER(word);"""

# Find the first main entry whose term begins with the prefix
# The ORDER BY is vital!
# Subtle- the :prefix is always of form '^abc*' so we need the 2nd char.
FIRST_FOR_PREFIX = """
SELECT eid FROM entries WHERE
    entries.peid = 0 AND
    LOWER(SUBSTR(entries.sortas, 1, 1)) = LOWER(SUBSTR(:prefix, 2, 1)) AND
    entries.eid IN
        (SELECT docid FROM term_words WHERE content MATCH :prefix)
    ORDER BY sortas LIMIT 1;
"""

# The ORDER BY is vital!
FIRST_FOR_LETTER = """
SELECT eid FROM entries
    WHERE LOWER(SUBSTR(sortas, 1, 1)) = LOWER(:letter) AND peid = 0
    ORDER BY sortas LIMIT 1;
"""

# It is much faster to use a subquery only for the needed rows with a
# main query that just picks up indents and eids.
# It is also much faster to compare a pre-computed sortas than to apply
# a collation function to the term.
ENTRIES_CACHE_EIDS = """
SELECT indent, eid FROM entries_cache ORDER BY cid
    LIMIT :limit OFFSET :offset;"""
ENTRY_EIDS = """
WITH RECURSIVE
    tree(eid, indent, sortas) AS (
        VALUES(:peid, -1, '')
        UNION ALL
        SELECT entries.eid, tree.indent + 1 AS depth, entries.sortas
            FROM entries JOIN tree ON entries.peid = tree.eid
            ORDER BY depth DESC, entries.sortas
            LIMIT :limit OFFSET :offset
    )
    SELECT indent, eid FROM tree;
"""

UNORDERED_PAGES = "SELECT eid, pages FROM entries WHERE eid != 0;"

GET_SUBENTRIES = "SELECT eid FROM entries WHERE peid = :peid;"

GET_MAIN_ENTRIES = """
SELECT eid FROM entries WHERE peid = 0 ORDER BY sortas;
"""

ENTRIES_WITH_PAGES = """
SELECT eid, saf, sortas, term, pages, notes, peid FROM entries
    WHERE eid != 0 AND pages IS NOT NULL AND LENGTH(pages) > 0;
"""

OUTPUT_ENTRIES = """
WITH RECURSIVE
    tree(eid, indent, sortas, term, pages) AS (
        VALUES(0, -1, '', '', '')
        UNION ALL
        SELECT entries.eid, tree.indent + 1 AS depth, entries.sortas,
               entries.term, entries.pages
            FROM entries JOIN tree ON entries.peid = tree.eid
            ORDER BY depth DESC, entries.sortas
    )
    SELECT indent, eid, term, pages, sortas FROM tree WHERE eid != 0;
"""
OUTPUT_XREFS = """
SELECT kind, toterm, to_eid FROM (
    SELECT kind, term AS toterm, to_eid
        FROM entries, xrefs
        WHERE entries.eid = xrefs.to_eid AND xrefs.from_eid = :eid
    UNION
    SELECT kind, generic_xrefs.term AS toterm, 0 AS to_eid
        FROM entries, generic_xrefs
        WHERE entries.eid = :eid AND from_eid = :eid
) ORDER BY kind, {sortAs}(toterm);
"""

MARKUP_FIELD = "SELECT {} FROM markup WHERE extension = :extension;"
MARKUPS = "SELECT extension FROM markup ORDER BY LOWER(extension);"

BOOKMARKS = """
SELECT eid, term, peid = 0 AS istop FROM entries
    WHERE eid IN (SELECT eid FROM bookmarks) ORDER BY sortas, peid;
"""
HAS_BOOKMARKS = "SELECT COUNT(*) FROM bookmarks;"

HAS_BOOKMARK = """
SELECT EXISTS (SELECT 1 FROM bookmarks WHERE eid = :eid LIMIT 1);
"""

GET_SORTAS_DATA = """
SELECT eid, CASE peid WHEN 0 THEN 1 ELSE 0 END AS istop, term, saf, sortas
    FROM entries WHERE eid != 0;"""

UPDATE_SORTAS_DATA = """
UPDATE entries SET sortas = :sortas WHERE eid = :eid;"""

GET_AUTO_REPLACE = """
SELECT replacement FROM auto_replace WHERE word = :word LIMIT 1;"""
# For Pair List Form
SORTED_AUTO_REPLACE = """
SELECT word, replacement FROM auto_replace ORDER BY LOWER(word);"""
AUTO_REPLACE_COUNT = "SELECT COUNT(*) FROM auto_replace;"

GET_ALL_GROUPS = """
SELECT gid, name, linked FROM groups ORDER BY LOWER(name);"""
GET_NORMAL_GROUPS = """
SELECT gid, name FROM groups WHERE linked = 0 ORDER BY LOWER(name);"""
GET_LINKED_GROUPS = """
SELECT gid, name FROM groups WHERE linked = 1 ORDER BY LOWER(name);"""
GET_GROUP_NAME = "SELECT name FROM groups WHERE gid = :gid;"
GET_ENTRY_GROUPS = """
SELECT gid, name FROM groups WHERE gid IN
    (SELECT gid FROM grouped WHERE eid = :eid) ORDER BY LOWER(name);
"""
GET_ENTRY_GROUPS_WITH_LINKS = """
SELECT gid, name, linked FROM groups WHERE gid IN
    (SELECT gid FROM grouped WHERE eid = :eid) ORDER BY LOWER(name);
"""
EIDS_FOR_GROUPS = "SELECT eid FROM grouped WHERE gid = :gid;"
GROUP_MEMBER_COUNT = "SELECT COUNT(*) FROM grouped WHERE gid = :gid;"
GET_GID_FOR_NAME = "SELECT gid FROM groups WHERE name = :name;"
IN_GROUP = "SELECT EXISTS (SELECT 1 FROM grouped WHERE eid = :eid LIMIT 1);"
NORMAL_GROUP_COUNT = "SELECT COUNT(*) FROM groups WHERE linked = 0;"
LINKED_GROUP_COUNT = "SELECT COUNT(*) FROM groups WHERE linked = 1;"
DELETED_GIDS = "SELECT gid FROM deleted_grouped WHERE eid = :eid;"
LINKED_GROUP = """
SELECT groups.gid FROM groups, grouped WHERE linked = 1 AND
    groups.gid = grouped.gid AND grouped.eid = :eid;
"""
IS_LINKED_GROUP = "SELECT linked FROM groups WHERE gid = :gid;"

UNINDEXED_PAGES = """
SELECT DISTINCT number FROM page_numbers_sequence
    WHERE number NOT IN (
        SELECT number FROM page_numbers_sequence, pages_words
        WHERE pages_words MATCH number)
    AND number <= :highestpage;
"""
