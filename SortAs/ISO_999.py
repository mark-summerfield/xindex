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
    registerRules, delete_ignored_firsts, padded_number, spelled_number,
    LETTERS_OR_DIGITS_OR_PUNCT, PUNCTUATION_AS_SPACE_RX)


PUNCTUATION_TO_IGNORE_RX = re.compile(r"[\\.,;:\[\]<>{}'\"‘’“”!?]+")


@registerRules
@functools.lru_cache(maxsize=None)
def wordByWordISO999en(term, saf=Saf.AUTO_NUMBER_ROMAN, *,
                       pad_digits=DEFAULT_PAD_DIGITS, ignored=None):
    """Word by Word (ISO 999 — English) «ISO by Word»

    """
    # Rules
    #   8.1 casefold; strip accents (for English)       [1] [2]
    #       convert punctuation to space                [4]
    #       drop punctuation                            [5]
    #       ignore ignored symbols                      [7]
    #   8.3 arrange only the first word numerically     [6]
    #   8.6 optionally drop specified first words       [3]

    numbers, roman_numerals, spell_numbers = Saf.flags(saf)
    if not numbers:
        pad_digits = 0

    text = Lib.htmlToPlainText(term).casefold()         # [1]
    text = delete_ignored_firsts(text, ignored)         # [3]
    text = Normalize.normalize(text)                    # [2]
    chars = []                                          # [7]
    for c in text:
        if unicodedata.category(c) in LETTERS_OR_DIGITS_OR_PUNCT:
            chars.append(c)
    text = "".join(chars)
    text = PUNCTUATION_TO_IGNORE_RX.sub("", text)       # [5]
    text = PUNCTUATION_AS_SPACE_RX.sub(" ", text)       # [4]
    if numbers:                                         # [6]
        words = []
        for i, word in enumerate(text.split()):
            if i == 0: # First word only
                if spell_numbers:
                    number = spelled_number(word, roman_numerals)
                    ok = True
                else:
                    number, ok = padded_number(word, roman_numerals,
                                               pad_digits)
                words.append(str(number) if ok else word)
            else:
                words.append(word)
        text = " ".join(words)
    return text


@registerRules # No cache since the underlying function is cached
def letterByLetterISO999en(term, saf=Saf.AUTO_NUMBER_ROMAN, *,
                           pad_digits=DEFAULT_PAD_DIGITS, ignored=None):
    """Letter by Letter (ISO 999 — English) «ISO by Letter»

    """
    return "".join(wordByWordISO999en(term, saf, pad_digits=pad_digits,
                                      ignored=ignored).split())
