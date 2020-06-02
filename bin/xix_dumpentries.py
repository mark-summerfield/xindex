#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import Xix
from Const import EntryDataKind


def main():
    if len(sys.argv) == 1 or sys.argv[1] in {"-h", "--help"}:
        raise SystemExit("usage: {} file.xix".format(
                         os.path.basename(sys.argv[0])))
    with Xix.Xix.Xix(sys.argv[1]) as xix:
        for entry in xix.entries(entryData=EntryDataKind.ALL_DATA):
            indent = " " * 5 * entry.indent
            print("{}{:04d} {} → {}".format(indent, entry.eid, entry.term,
                  entry.pages))
            for xref in xix.xrefs(entry.eid):
                print(indent, "   ", xref)
            for xref in xix.generic_xrefs(entry.eid):
                print(indent, "   ", xref)


if __name__ == "__main__":
    main()
