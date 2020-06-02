#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import re

import roman


AT_PAGE_RX = re.compile(r"@([0-9]+)(?:\.[0-9]+)*$")
DIGIT_RX = re.compile(r"^[0-9]+$")
LEADING_DIGITS_RX = re.compile(r"^([0-9]+)")
LEADING_ROMAN_RX = re.compile(r"^([cdilmvxCDILMVX]+)\b")

ROMAN_OFFSET = 1000
INTEGER_OFFSET = 10000
SORT_VALUE_COMPONENT_COUNT = 8


class Error(Exception):
    pass


def isdigit(text):
    return DIGIT_RX.match(text) is not None


def valueOf(text, *, addOffset=False):
    if not text:
        return 0
    if isdigit(text):
        return int(text) + (INTEGER_OFFSET if addOffset else 0)
    if isdigit(text[0]):
        match = LEADING_DIGITS_RX.search(text)
        if match is not None:
            return int(match.group(1)) + (
                INTEGER_OFFSET if addOffset else 0)
    if text[0] in "cdilmvxCDILMVX":
        match = LEADING_ROMAN_RX.search(text)
        if match is not None:
            try:
                return (roman.fromRoman(match.group(1).upper()) +
                        (ROMAN_OFFSET if addOffset else 0))
            except roman.RomanError:
                pass
    match = AT_PAGE_RX.search(text)
    if match is not None:
        return int(match.group(1)) + (INTEGER_OFFSET if addOffset else 0)
    # return None
