#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import copy
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tests.pages
import Pages


def print_pages(pages):
    for page in pages:
        for depth, child in page.iterate():
            print("{}{}".format("→ " * (depth + 1), child))
    print()


start = 0
end = len(tests.pages.PAGESPAIRS2)
if len(sys.argv) > 1:
    start = int(sys.argv[1])
    if len(sys.argv) > 2:
        end = int(sys.argv[2])
pageRange = Pages.pageRangeCMS16
pairs = tests.pages.PAGESPAIRS2
for i, (original, expected) in enumerate(pairs[start:end]):
    parser = Pages.Parser.Parser()
    parser.feed("<p>{}</p>".format(original))
    print("=" * 20)
    print()
    print_pages(parser.pages)
    pages = parser.toHtml(pageRange=pageRange)
    print("U", original)
    print()
    print("S", pages)
    parser = Pages.Parser.Parser()
    parser.feed("<p>{}</p>".format(pages))
    samePages = copy.deepcopy(parser.pages)
    same = parser.toHtml(pageRange=pageRange)
    if same != pages:
        print("\nFAILED TO ROUND TRIP #{}\n".format(i))
        print("R", same)
        print()
        # print_pages(samePages)
