#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import functools
import logging

import Lib
from . import PageRange
from . import Parser


@functools.lru_cache(maxsize=None)
def searchablePages(pages):
    """Accepts plain text or HTML pages and returns a string suitable
    for FTS4. See test_Pages.py for examples.
    """
    if pages is None or not pages.strip():
        return ""
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        # Must use PageRange.pageRangeFull (i.e., full page numbers)
        return parser.toPlainText(pageRange=PageRange.pageRangeFull)
    except Exception as err:
        logging.error("Pages.searchablePages failed: {}".format(err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def sortedPages(pages, pageRange=PageRange.pageRangeCMS16):
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        return parser.toHtml(pageRange=pageRange)
    except Exception as err:
        logging.error("Pages.sortedPages failed: {}".format(err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def mergedPages(*pages, pageRange=None):
    return combinedOverlappingPages(
        ", ".join(page for page in pages if page is not None), pageRange)


@functools.lru_cache(maxsize=None)
def hasOverlappingPages(pages):
    """Accepts plain text or HTML pages and returns True if there are
    overlapping pages.
    """
    if pages is None or not pages.strip():
        return False
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        return parser.hasOverlappingPages()
    except Exception as err:
        logging.error("Pages.hasOverlappingPages failed: {}".format(err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def combinedOverlappingPages(pages, pageRange=PageRange.pageRangeCMS16):
    """Accepts plain text or HTML pages and returns the pages as HTML
    with no overlapping pages.
    """
    if pages is None or not pages.strip():
        return ""
    parser = Parser.Parser()
    try:
        parser.feed(sortedPages(pages))
        pages = parser._combinedOverlappingPages()
        return sortedPages(pages, pageRange=pageRange)
    except Exception as err:
        logging.error("Pages.combinedOverlappingPages failed: {}".format(
                      err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def toIndividualHtmlPages(pages, pageRange=PageRange.pageRangeCMS16):
    """Accepts plain text or HTML pages and returns a possibly empty
    list of HTML pages.
    """
    if pages is None or not pages.strip():
        return []
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        return parser.toIndividualHtmlPages(pageRange=pageRange)
    except Exception as err:
        logging.error("Pages.toIndividualHtmlPages failed: {}".format(err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def renumbered(pages, options, pageRange=PageRange.pageRangeCMS16):
    """Accepts plain text or HTML pages and returns a possibly
    renumbered pages.
    """
    if pages is None or not pages.strip():
        return ""
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        return parser.renumbered(options, pageRange=pageRange)
    except Exception as err:
        logging.error("Pages.renumbered failed: {}".format(err))
        return Lib.htmlToPlainText(pages)


@functools.lru_cache(maxsize=None)
def highestPage(pages):
    """Accepts plain text or HTML pages and returns the highest page
    number or 0 if pages is empty.
    """
    if pages is None or not pages.strip():
        return 0
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        pairs = parser.asNumberPairs()
        return max(max(start, end) for start, end in pairs)
    except Exception as err:
        logging.error("Pages.highestPage failed: {}".format(err))
        return 0


@functools.lru_cache(maxsize=None)
def largestPageRange(pages):
    """Accepts plain text or HTML pages and returns the maximum page
    range span or 0 if pages is empty or there are no ranges.
    """
    if pages is None or not pages.strip():
        return 0
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        pairs = parser.asNumberPairs()
        largest = 0
        for start, end in pairs:
            if end != 0:
                diff = end - start + 1
                if diff > largest:
                    largest = diff
        return largest
    except Exception as err:
        logging.error("Pages.largestPageRange failed: {}".format(err))
        return 0


@functools.lru_cache(maxsize=None)
def pagesCount(pages):
    """Accepts plain text or HTML pages and returns the number of pages
    and page ranges, or 0 if pages is empty.
    """
    if pages is None or not pages.strip():
        return 0
    parser = Parser.Parser()
    try:
        parser.feed(pages)
        return parser.count()
    except Exception as err:
        logging.error("Pages.pagesCount failed: {}".format(err))
        return 0
