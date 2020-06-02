#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import functools
import re
import unicodedata

import Lib
import Normalize
import Saf
from Const import DEFAULT_PAD_DIGITS
from .Common import (
    registerRules, padded_number, delete_ignored_firsts,
    LETTERS_OR_DIGITS, LETTERS_OR_DIGITS_OR_PUNCT,
    PUNCTUATION_AS_SPACE_RX)


PUNCTUATION_TO_IGNORE1_RX = re.compile(r"[\\;:()\[\]<>{}'\"‘’“”!?]+")
PUNCTUATION_TO_IGNORE2_RX = re.compile(r"[.,]+")
DIGITS_RX = re.compile(r"(?<!\d)(\.\d+)")
FIX_CHAR_AFTER_NUMBER_RX = re.compile(
    r"(?P<dec>\d+)(?P<nondec>\D+)\.(?P<frac>\d+)")


@registerRules # No cache since the underlying function is cached
def letterByLetterNISO3(term, saf=Saf.AUTO_NUMBER_ROMAN, *,
                        pad_digits=DEFAULT_PAD_DIGITS, ignored=None):
    """Letter by Letter (NISO Technical Report 3) «NISO by Letter»

    Basic order: spaces, symbols, digits, letters.

    These rules are not recommended by NISO except when updating an
    existing index that uses letter by letter ordering.
    """
    text = wordByWordNISO3(term, saf, pad_digits=pad_digits,
                           ignored=ignored)
    return "".join(text.split()) # Strip out whitespace


@registerRules
@functools.lru_cache(maxsize=None)
def wordByWordNISO3(term, saf=Saf.AUTO_NUMBER_ROMAN, *,
                    pad_digits=DEFAULT_PAD_DIGITS, ignored=None):
    """Word by Word (NISO Technical Report 3) «NISO by Word»

    Basic order: spaces, symbols, digits, letters.
    """
    # The NISO 3 comprehensive example does not use ASCII order for
    # symbols; also it does not follow strict numerical order, e.g.,
    # putting 007 before 1 2 3. This rule implementation follows the NISO
    # 3 rules correctly even when this differs from the example.
    #
    # Rules:
    #   3.1 Normalize spaces                        [1]
    #   3.2 Punctutation → space                    [2]
    #   3.3 Punctutation ignored                    [3a] [3b]
    #   3.4 Symbols (two+ treated as first)         [4]
    #   3.5 Numbers before letters (works as-is) & don't spell numbers [8]
    #   3.6 Upper- and lower-case equal             [6]
    #   3.6.1 Expand ligatures, combined letters, and strip accents [7]
    #   3.7 Super- and sub-scripts as normal chars  [6]
    #   4.5 & 4.6 Leading articles shouldn't normally be ignored but can
    #       be if the user requires                 [11]
    #   6 Numbers                                   [9]
    #   6.3 Preserve decimal point if needed        [10]
    #   7.1 Symbols are in ASCII order
    numbers, roman_numerals, _ = Saf.flags(saf) # Ignore spell_numbers
    if not numbers:
        pad_digits = 0
    text = Lib.htmlToPlainText(term).casefold()         # [6]
    text = delete_ignored_firsts(text, ignored)         # [10]
    text = Normalize.normalize(text)                    # [7]
    chars = []                                          # [4]
    inSymbols = False
    for c in text:
        if unicodedata.category(c) not in LETTERS_OR_DIGITS_OR_PUNCT:
            if inSymbols:
                continue
            inSymbols = True
        else:
            inSymbols = False
        chars.append(c)
    text = "".join(chars)
    text = PUNCTUATION_TO_IGNORE1_RX.sub("", text)      # [3a]
    text = PUNCTUATION_AS_SPACE_RX.sub(" ", text)       # [2]
    if numbers:                                         # [9]
        text = DIGITS_RX.sub(r"0\1", text).replace(",", "")
        words = []
        for word in text.split():
            parts = word.split(".")
            if len(parts) == 2:
                dec, ok = padded_number(parts[0], roman_numerals,
                                        pad_digits)
                if not ok:
                    dec = "0"
                frac, ok = padded_number(parts[1], roman_numerals,
                                         pad_digits)
                number = "{}!{}".format(dec, frac)
            else:
                number, ok = padded_number(word, roman_numerals, pad_digits)
                if ok:
                    number += "!" + ("0" * pad_digits)
            words.append(str(number) if ok else word)
        text = " ".join(words)
    text = PUNCTUATION_TO_IGNORE2_RX.sub("", text)      # [3b]
    if numbers:
        text = text.replace("!", ".")                   # [10]
        text = FIX_CHAR_AFTER_NUMBER_RX.sub(r"\g<dec>.\g<frac>\g<nondec>",
                                            text)
    text = " ".join(text.split())                       # [1]
    chars = []
    for c in text:
        if (c not in " ." and unicodedata.category(c)
                not in LETTERS_OR_DIGITS):
            chars.append("!")
        chars.append(c)
    return "".join(chars)
