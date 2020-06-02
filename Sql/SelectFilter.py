#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import sys

from . import PageOrder


TERMS_MATCHING_EIDS = """
SELECT eid FROM entries WHERE entries.eid IN (
        SELECT docid FROM term_words WHERE content MATCH :match
    )
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
TERMS_MATCHING_COUNT = """
SELECT COUNT(*) FROM term_words WHERE content MATCH :match;
"""

NOTES_MATCHING_EIDS = """
SELECT eid FROM entries WHERE entries.eid IN (
        SELECT docid FROM note_words WHERE content MATCH :match
    )
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
NOTES_MATCHING_COUNT = """
SELECT COUNT(*) FROM note_words WHERE content MATCH :match;
"""

IN_NORMAL_GROUP_EIDS = """
SELECT entries.eid FROM entries, groups, grouped
    WHERE entries.eid = grouped.eid AND grouped.gid = :match
          AND groups.gid = grouped.gid AND groups.linked = 0
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
IN_NORMAL_GROUP_COUNT = """
SELECT COUNT(*) FROM entries, groups, grouped
    WHERE entries.eid = grouped.eid AND grouped.gid = :match
          AND groups.gid = grouped.gid AND groups.linked = 0;
"""

IN_LINKED_GROUP_EIDS = """
SELECT entries.eid FROM entries, groups, grouped
    WHERE entries.eid = grouped.eid AND grouped.gid = :match
          AND groups.gid = grouped.gid AND groups.linked = 1
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
IN_LINKED_GROUP_COUNT = """
SELECT COUNT(*) FROM entries, groups, grouped
    WHERE entries.eid = grouped.eid AND grouped.gid = :match
          AND groups.gid = grouped.gid AND groups.linked = 1;
"""

ENTRIES_WITH_PAGES_EIDS = """
SELECT eid FROM entries WHERE entries.eid IN (
        SELECT docid FROM pages_words WHERE content MATCH :match
    )
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
ENTRIES_WITH_PAGES_COUNT = """
SELECT COUNT(*) FROM pages_words WHERE content MATCH :match;
"""

CREATION_ORDER_EIDS = """
SELECT eid FROM entries WHERE eid != 0
    ORDER BY created DESC LIMIT :limit OFFSET :offset;
"""
UPDATED_ORDER_EIDS = """
SELECT eid FROM entries WHERE eid != 0
    ORDER BY updated DESC LIMIT :limit OFFSET :offset;
"""
UPDATED_ORDER_COUNT = CREATION_ORDER_COUNT = """
SELECT COUNT(*) FROM entries WHERE eid != 0;
"""

module = sys.modules[__name__]
for what in PageOrder.PAGE_ORDERS:
    name = "PAGES_ORDER_{}_".format(what.upper())
    key = name + "EIDS"
    value = """
SELECT docid FROM pages_words, page_numbers_{0}_sequence, entries
    WHERE pages_words MATCH page_numbers_{0}_sequence.number
    AND docid = entries.eid
    ORDER BY id, sortas, peid LIMIT :limit OFFSET :offset;
""".format(what)
    setattr(module, key, value)
    key = name + "COUNT"
    value = """
SELECT COUNT(*) FROM pages_words, page_numbers_{0}_sequence
    WHERE pages_words MATCH page_numbers_{0}_sequence.number;
""".format(what)
    setattr(module, key, value)
del what, module, key, value


PAGES_AND_SEE_XREF_EIDS = """
SELECT eid FROM entries
    WHERE eid != 0
    AND (pages IS NOT NULL AND TRIM(pages) != '')
    AND (eid IN (SELECT from_eid FROM xrefs WHERE kind = 1)
         OR eid IN (SELECT from_eid FROM generic_xrefs WHERE kind = 3))
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
PAGES_AND_SEE_XREF_COUNT = """
SELECT COUNT(*) FROM entries
    WHERE eid != 0
    AND (pages IS NOT NULL AND TRIM(pages) != '')
    AND (eid IN (SELECT from_eid FROM xrefs WHERE kind = 1)
         OR eid IN (SELECT from_eid FROM generic_xrefs WHERE kind = 3));
"""

NO_PAGES_AND_NO_SUBENTRIES_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (pages IS NULL OR TRIM(pages) = '')
        AND NOT EXISTS (
            SELECT child.peid FROM entries AS child
                WHERE child.peid = parent.eid)
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
NO_PAGES_AND_NO_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid FROM entries AS parent
        WHERE (pages IS NULL OR TRIM(pages) = '')
    AND NOT EXISTS (
        SELECT child.peid FROM entries AS child
            WHERE child.peid = parent.eid)
) WHERE eid != 0;
"""

NO_PAGES_NO_SUBENTRIES_NO_XREFS_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (pages IS NULL OR TRIM(pages) = '')
        AND NOT EXISTS (
            SELECT child.peid FROM entries AS child
                WHERE child.peid = parent.eid)
        AND NOT EXISTS (
            SELECT from_eid FROM xrefs WHERE from_eid = eid)
        AND NOT EXISTS (
            SELECT from_eid FROM generic_xrefs WHERE from_eid = eid)
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
NO_PAGES_NO_SUBENTRIES_NO_XREFS_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid FROM entries AS parent
        WHERE (pages IS NULL OR TRIM(pages) = '')
    AND NOT EXISTS (
        SELECT child.peid FROM entries AS child
            WHERE child.peid = parent.eid)
    AND NOT EXISTS (
        SELECT from_eid FROM xrefs WHERE from_eid = eid)
    AND NOT EXISTS (
        SELECT from_eid FROM generic_xrefs WHERE from_eid = eid)
) WHERE eid != 0;
"""

HAS_NO_SUBENTRIES_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE NOT EXISTS (
            SELECT child.peid FROM entries AS child
                WHERE child.peid = parent.eid)
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
HAS_NO_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE NOT EXISTS (
            SELECT child.peid FROM entries AS child
                WHERE child.peid = parent.eid)
) WHERE eid != 0;
"""
HAS_ONE_SUBENTRY_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) = 1
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
HAS_ONE_SUBENTRY_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) = 1
) WHERE eid != 0;
"""
HAS_TWO_SUBENTRIES_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) = 2
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
HAS_TWO_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) = 2
) WHERE eid != 0;
"""
HAS_SUBENTRIES_EIDS = """
SELECT eid FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) > 0
) WHERE eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
HAS_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM (
    SELECT eid, peid, sortas FROM entries AS parent
        WHERE (SELECT COUNT(*) FROM entries AS child
                WHERE child.peid = parent.eid) > 0
) WHERE eid != 0;
"""
HAS_NOTES_EIDS = """
SELECT eid FROM entries WHERE notes IS NOT NULL AND TRIM(notes) != ''
    AND eid != 0 ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
HAS_NOTES_COUNT = """
SELECT COUNT(*) FROM entries WHERE notes IS NOT NULL AND TRIM(notes) != ''
    AND eid != 0;
"""

NO_AUTOMATIC_SORT_AS_EIDS = """
SELECT eid FROM entries WHERE eid != 0 AND saf = 'c'
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""
NO_AUTOMATIC_SORT_AS_COUNT = """
SELECT COUNT(*) FROM entries WHERE eid != 0 AND saf = 'c';"""
HAS_SEE_OR_SEE_ALSO_EIDS = """
SELECT eid FROM entries WHERE eid IN (SELECT DISTINCT from_eid FROM xrefs)
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;"""
HAS_SEE_OR_SEE_ALSO_COUNT = """
SELECT COUNT(*) FROM entries
    WHERE eid IN (SELECT DISTINCT from_eid FROM xrefs);
"""
HAS_GENERIC_SEE_OR_SEE_ALSO_EIDS = """
SELECT eid FROM entries
    WHERE eid IN (SELECT DISTINCT from_eid FROM generic_xrefs)
    ORDER BY sortas, peid LIMIT :limit OFFSET :offset;"""
HAS_GENERIC_SEE_OR_SEE_ALSO_COUNT = """
SELECT COUNT(*) FROM entries
    WHERE eid IN (SELECT DISTINCT from_eid FROM generic_xrefs);
"""

FIRST_SUBENTRIES_EIDS = """
SELECT eid FROM entries WHERE peid IN (
    SELECT main.eid FROM entries AS main WHERE main.peid = 0)
ORDER BY entries.sortas LIMIT :limit OFFSET :offset;
"""
FIRST_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM entries WHERE peid IN (
    SELECT main.eid FROM entries AS main WHERE main.peid = 0);
"""

SECOND_SUBENTRIES_EIDS = """
SELECT eid FROM entries WHERE peid IN (
    SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
        SELECT main.eid FROM entries AS main WHERE main.peid = 0)
)
ORDER BY entries.sortas LIMIT :limit OFFSET :offset;
"""
SECOND_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM entries WHERE peid IN (
    SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
        SELECT main.eid FROM entries AS main WHERE main.peid = 0)
);
"""

THIRD_SUBENTRIES_EIDS = """
SELECT eid FROM entries WHERE peid IN (
    SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
        SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
            SELECT main.eid FROM entries AS main WHERE main.peid = 0)
)) ORDER BY entries.sortas LIMIT :limit OFFSET :offset;
"""
THIRD_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM entries WHERE peid IN (
    SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
        SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
            SELECT main.eid FROM entries AS main WHERE main.peid = 0)
));
"""

FOURTH_SUBENTRIES_EIDS = """
SELECT eid FROM entries WHERE peid IN (
    SELECT sub3.eid FROM entries AS sub3 WHERE sub3.peid IN (
        SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
            SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
                SELECT main.eid FROM entries AS main WHERE main.peid = 0)
))) ORDER BY entries.sortas LIMIT :limit OFFSET :offset;
"""
FOURTH_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM entries WHERE peid IN (
    SELECT sub3.eid FROM entries AS sub3 WHERE sub3.peid IN (
        SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
            SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
                SELECT main.eid FROM entries AS main WHERE main.peid = 0)
)));
"""

FIFTH_SUBENTRIES_EIDS = """
SELECT eid FROM entries WHERE peid IN (
    SELECT sub4.eid FROM entries AS sub4 WHERE sub4.peid IN (
        SELECT sub3.eid FROM entries AS sub3 WHERE sub3.peid IN (
            SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
                SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
                    SELECT main.eid FROM entries AS main WHERE main.peid = 0)
)))) ORDER BY entries.sortas LIMIT :limit OFFSET :offset;
"""
FIFTH_SUBENTRIES_COUNT = """
SELECT COUNT(*) FROM entries WHERE peid IN (
    SELECT sub4.eid FROM entries AS sub4 WHERE sub4.peid IN (
        SELECT sub3.eid FROM entries AS sub3 WHERE sub3.peid IN (
            SELECT sub2.eid FROM entries AS sub2 WHERE sub2.peid IN (
                SELECT sub1.eid FROM entries AS sub1 WHERE sub1.peid IN (
                    SELECT main.eid FROM entries AS main WHERE main.peid = 0)
))));
"""

HAS_OVERLAPPING_PAGES_CACHE_EIDS = """
SELECT eid FROM overlapping_pages_cache ORDER BY cid
    LIMIT :limit OFFSET :offset;"""
HAS_OVERLAPPING_PAGES_EIDS = """
SELECT eid FROM entries WHERE hasOverlappingPages(pages)
ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""

HAS_OVERLAPPING_PAGES_COUNT = """
SELECT COUNT(*) FROM entries WHERE hasOverlappingPages(pages);
"""

TOO_HIGH_PAGE_EIDS = """
SELECT eid FROM entries, pages_words
    WHERE highestPage(pages_words.content) > :match
    AND entries.eid = pages_words.docid
ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""

TOO_HIGH_PAGE_COUNT = """
SELECT COUNT(*) FROM entries, pages_words
    WHERE highestPage(pages_words.content) > :match
    AND entries.eid = pages_words.docid;
"""

TOO_LARGE_PAGE_RANGE_EIDS = """
SELECT eid FROM entries WHERE largestPageRange(pages) > :match
ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""

TOO_LARGE_PAGE_RANGE_COUNT = """
SELECT COUNT(*) FROM entries WHERE largestPageRange(pages) > :match;
"""

TOO_MANY_PAGES_EIDS = """
SELECT eid FROM entries WHERE pagesCount(pages) > :match
ORDER BY sortas, peid LIMIT :limit OFFSET :offset;
"""

TOO_MANY_PAGES_COUNT = """
SELECT COUNT(*) FROM entries WHERE pagesCount(pages) > :match;
"""

SAME_TERM_TEXTS_CACHE_EIDS = """
SELECT eid FROM same_term_texts_cache ORDER BY cid
    LIMIT :limit OFFSET :offset;"""
SAME_TERM_TEXTS_EIDS = """
SELECT entries1.eid FROM entries AS entries1, entries AS entries2
    WHERE entries1.eid != 0 AND entries2.eid != 0
      AND entries1.eid != entries2.eid
      AND entries1.peid = entries2.peid
      AND htmlToCanonicalText(entries1.term) =
          htmlToCanonicalText(entries2.term)
ORDER BY entries1.sortas, entries1.peid LIMIT :limit OFFSET :offset;
"""

SAME_TERM_TEXTS_COUNT = """
SELECT COUNT(*) FROM entries AS entries1, entries AS entries2
    WHERE entries1.eid != 0 AND entries2.eid != 0
      AND entries1.eid != entries2.eid
      AND entries1.peid = entries2.peid
      AND htmlToCanonicalText(entries1.term) =
          htmlToCanonicalText(entries2.term);
"""
