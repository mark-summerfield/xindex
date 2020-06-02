#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import gzip
import os
import random
import re
import sys

import roman

import Lib
import Pages
import Saf
import Sql
import SortAs
import Xix
from Config import Gopt
from Const import LanguageKind, UTF8


WORD_FILE = "misc/american-english.gz"


def main():
    # random.seed(917)
    count = 5000
    filename = None
    if len(sys.argv) > 1:
        if sys.argv[1] in {"-h", "--help"}:
            raise SystemExit("usage: {} count [filename]".format(
                             os.path.basename(sys.argv[0])))
        count = int(sys.argv[1])
        if len(sys.argv) > 2:
            filename = sys.argv[2]
            if not filename.endswith(".xix"):
                filename += ".xix"

    xix, filename = create_xix(count, "MakeTest", filename, )
    try:
        count = populate_xix(count, xix)
    finally:
        if xix is not None:
            xix.close()
    print("\nCreated '{}' with {:,} entries".format(filename, count))


def create_xix(count, username, filename=None,
               language=LanguageKind.AMERICAN):
    if filename is None:
        filename = "{}.xix".format(count)
    try:
        os.remove(filename)
    except OSError:
        pass
    return (Xix.Xix.Xix(filename, username, language), filename)


def populate_xix(count, xix):
    xix._cache_clear()
    with Lib.Transaction.Transaction(xix) as cursor:
        for entry, xrefs in make_fake_entries(count):
            d = entry.__dict__.copy()
            # print("[{}]".format(entry.pages))
            cursor.execute(Sql.REINSERT_ENTRY, d)
            for xref in xrefs:
                add_xref(cursor, xref)
        return Sql.first(cursor, """SELECT COUNT(*) FROM entries
WHERE peid IS NOT NULL""", default=0)


def replacer(match):
    text = match.group(1)
    if not text:
        text = match.group(2)
    return "'{}".format(text.lower())


def make_fake_entries(count):
    with gzip.open(WORD_FILE, "rt", encoding=UTF8) as file:
        words = [word.strip() for word in file if len(word.strip()) > 1]
    fortyPercent = round(40 * (count / 100))
    for index in range(count):
        term = []
        for _ in range(random.choice((1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 5,
                       6, 7))):
            try:
                word = re.sub(r"(?<=\w\w)'([A-Z])|'([A-Z])(?=\w\w)",
                              replacer, random.choice(words).casefold())
                term.append(word)
            except IndexError:
                raise StopIteration
        for j in range(len(term)):
            word = term[j]
            if "'" in word:
                word = word.replace("'", "\u2019")
            elif random.randint(1, 10) == 1:
                word = word.title()
            term[j] = possiblyDecorated(word)
        term = " ".join(term)
        saf = (Saf.AUTO if random.randint(1, 100) != 1 else
               random.choice(Saf.COMBINATIONS))
        sortas = SortAs.wordByWordCMS16(Lib.htmlToPlainText(term))
        pages = []
        for _ in range(11):
            if random.randint(1, 50) == 1:
                maximum = 25 if random.randint(1, 5) == 1 else 10
                page = roman.toRoman(random.randint(1, maximum))
                if random.choice((0, 1)):
                    page = page.lower()
            else:
                if random.randint(1, 6) == 1:
                    first = random.randint(1, 490)
                    second = first + random.randint(1, 10)
                    page = "{}-{}".format(first, second)
                else:
                    page = str(random.randint(1, 500))
            pages.append(possiblyDecorated(page, 100, True))
        pages = Pages.sortedPages(",".join(pages))
        peid = 0 if index < fortyPercent else random.randint(1, index)
        xrefs = []
        eid = index + 1
        if eid > 10 and random.randint(1, 10) == 1:
            seen = set()
            for _ in range(random.randint(1, 5)):
                to_eid = random.randint(1, eid - 1)
                if to_eid != eid and to_eid not in seen:
                    xrefs.append((eid, to_eid, None, random.choice((1, 2))))
                    seen.add(to_eid)
        if random.randint(1, 50) == 1:
            xrefs.append((eid, None, "generic #{}".format(eid),
                         random.choice((3, 4))))
        notes = "Note #{:,}".format(eid)
        yield (Xix.Util.Entry(eid, saf, sortas, term, pages,
                              notes, peid=peid), xrefs)


def possiblyDecorated(text, factor=50, addToNumber=False):
    if random.randint(1, factor) == 1:
        text = "<b>{}</b>".format(text)
    if random.randint(1, factor) == 1:
        text = "<i>{}</i>".format(text)
    if random.randint(1, factor) == 1:
        text = ('<span style="font-size: 11pt; '
                'font-family: \'{}\';">{}</span>').format(Gopt.AltFont,
                                                          text)
    elif random.randint(1, factor) == 1:
        text = ('<span style="font-size: 11pt; '
                'font-family: \'{}\';">{}</span>').format(Gopt.MonoFont,
                                                          text)
    if addToNumber:
        factor //= 3
        if random.randint(1, factor) == 1:
            text += "<sup>{}</sup>".format(random.choice("abcdef"))
        elif random.randint(1, factor) == 1:
            text += "<sub>{}</sub>".format(random.randint(1, 5))
        elif random.randint(1, factor) == 1:
            text += "<b>t</b>"
        elif random.randint(1, factor) == 1:
            text += "<i>f</i>"
    return text


def add_xref(cursor, xref):
    if xref[-1] in {1, 2}:
        cursor.execute("""INSERT INTO xrefs (from_eid, to_eid, kind)
VALUES (?, ?, ?);""", (xref[0], xref[1], xref[-1]))
    else:
        cursor.execute("""INSERT INTO generic_xrefs (from_eid, term, kind)
VALUES (?, ?, ?);""", (xref[0], xref[2], xref[-1]))



if __name__ == "__main__":
    main()
