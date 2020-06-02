#!/usr/bin/env python3
# Copyright © 2016-20 Qtrac Ltd. All rights reserved.


CREATE_PAGE_NUMBERS_SEQUENCE = """
DROP TABLE IF EXISTS page_numbers_sequence;

CREATE TEMP TABLE page_numbers_sequence (
    number INTEGER PRIMARY KEY NOT NULL
);

"""
INSERT_PAGE_NUMBERS_SEQUENCE = """
INSERT INTO page_numbers_sequence (number) VALUES (?);"""


CREATE_PAGE_NUMBER_SEQUENCE = """
DROP TABLE IF EXISTS page_numbers_{0}_sequence;

CREATE TEMP TABLE page_numbers_{0}_sequence (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    number TEXT -- text page number
);

"""
INSERT_PAGE_NUMBER_SEQUENCE = """
INSERT INTO page_numbers_{}_sequence (number) VALUES (?);"""


PAGE_ORDERS = ( # Must match Const/Kinds.py PagesOrderKind
    "ritoxlix",
    "rltoc",
    "d1to49",
    "d50to99",
    "d100to149",
    "d150to199",
    "d200to249",
    "d250to299",
    "d300to349",
    "d350to399",
    "d400to449",
    "d450to499",
    "d500to599",
    "d600to699",
    "d700to799",
    "d800to899",
    "d900to999",
    "d1000to1199",
    "d1200to1399",
    "d1400to1599",
    "d1600to1799",
    "d1800to2000",
    )
