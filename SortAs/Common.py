#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import collections
import functools
import re

import roman

import Lib
import Saf
from Const import (
    DEFAULT_PAD_DIGITS, DELETE_IGNORED_FIRSTS_TEMPLATE, EN_DASH)


RulesForName = collections.OrderedDict()
registerRules = functools.partial(Lib.registerRules, RulesForName,
                                  reorder=True)


"""
If spell_numbers is True, if the first word is a decimal whole
number it is converted to its spelled out form, e.g., 12 will be
converted to twelve. And if roman_numerals is True and the first word
is a roman number, the same applied, e.g., XIV will be converted to
fourteen.

If pad_digits is nonzero, numbers are converted to be that width. For
example, with pad_digits = 4, 85, 139, and 2015 will be converted to
0004, 0085, 0139, and 2015.

If roman_numerals is True (and pad_digits is nonzero), then roman
numbers are converted to decimals and padded. For example, Henry
VIII will become Henry 0008.

spell_numbers is only applied to the first word.
"""

WORD_SEP_RX = re.compile(r"[-" + EN_DASH + r"/]")
O_APOSTROPHE_RX = re.compile(r"o['\u2019](?=[a-z])")
APOSTROPHE_S_RX = re.compile(r"['\u2019]s\b")
FINAL_DIGITS_RX = re.compile(r"([0-9]+)$")
NOT_LETTERS_OR_DIGITS_RX = re.compile(r"[^0-9a-z]")

# All hyphens + slash (assumes we normalize first)
PUNCTUATION_AS_SPACE_RX = re.compile(r"[-/]")

DIGITS_INSIDE_RX = re.compile(r"([0-9]+)")

LETTERS_OR_DIGITS = frozenset({"LC", "Ll", "Lt", "Lu", "Nd"})
LETTERS_OR_DIGITS_OR_PUNCT = frozenset(
    LETTERS_OR_DIGITS | {"Pc", "Pd", "Pe", "Pf", "Pi", "Ps", "Zs"})


def padded_number(word, roman_numerals, pad_digits):
    fmt = "{{:0{}}}".format(pad_digits)
    if roman_numerals:
        try:
            n = roman.fromRoman(word.upper())
            word = fmt.format(n)
            return word, True
        except roman.RomanError: # Isn't a roman number
            pass
    padder = lambda match: fmt.format(int(match.group(1)))
    word, n = DIGITS_INSIDE_RX.subn(padder, word)
    return word, bool(n)


def spelled_number(word, roman_numerals):
    if word.isdigit():
        return Lib.spellNumber(int(word))
    elif roman_numerals:
        try:
            n = roman.fromRoman(word.upper())
            return Lib.spellNumber(n)
        except roman.RomanError: # Isn't a roman number
            pass
    return word


def delete_ignored_firsts(term, ignore): # term must be plain text
    if ignore:
        return re.sub(DELETE_IGNORED_FIRSTS_TEMPLATE.format(
            "|".join(re.escape(word) for word in ignore)), "", term)
    return term
# See also: Xix/_Model2.py deleteIgnoredFirstWords()


Candidate = collections.namedtuple("Candidate", "candidate saf")


def candidatesFor(term, rulesName, ignored, pad_digits=DEFAULT_PAD_DIGITS,
                  suggest_spelled=True):
    sortBy = RulesForName[rulesName].function
    candidates = []
    safs = []
    for saf in Saf.COMBINATIONS:
        if not suggest_spelled and saf == Saf.AUTO:
            continue
        candidate = sortBy(term, saf, pad_digits=pad_digits,
                           ignored=ignored)
        if candidate not in candidates:
            candidates.append(candidate)
            safs.append(saf)
    return sorted((Candidate(candidate, saf) for candidate, saf in
                   zip(candidates, safs)), key=lambda c: Saf.key(c.saf))
