#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import functools

import Lib
import Normalize
import Saf
from Const import DEFAULT_PAD_DIGITS
from .Common import (
    registerRules, padded_number, spelled_number, delete_ignored_firsts,
    WORD_SEP_RX, O_APOSTROPHE_RX, APOSTROPHE_S_RX, FINAL_DIGITS_RX,
    NOT_LETTERS_OR_DIGITS_RX)


@registerRules
@functools.lru_cache(maxsize=None)
def letterByLetterCMS16(term, saf=Saf.AUTO, *,
                        pad_digits=DEFAULT_PAD_DIGITS, ignored=None):
    """Letter by Letter (Chicago Manual of Style) «CMS by Letter»

    Converts a term to a "sort as" text that when sorted "naturally"
    will give the letter by letter ordering specified in Chicago 16th
    edition 16.60.

    The captial letter that may appear between the first and second word
    is used to force the correct order of precedence.
    """
    # ignored should be None or an empty set for main entries, and a
    # set of articles, conjunctions, and prepositions to ignore for
    # subentries.
    #
    # Rules (all words):
    #     casefold                                  [1]
    #     strip accents                             [2]
    #     aword-bword           -> awordbword       [3]
    #     delete non-letters and non-digits         [4]
    #     O'Name                -> oname            [9]
    # Precedence (first word only):
    #     word                  -> word             [5]
    #     word (.*              -> word D .*        [6]
    #     word, .*              -> word H .*        [7]
    #     word\s*[,;:.]*\d+.*   -> word P \d+.*     [8]
    # Subentries: remove leading articles,          [10]
    #   conjunctions, and prepositions.
    # Extensions:
    #     word's                -> words            [X1]

    numbers, roman_numerals, spell_numbers = Saf.flags(saf)
    if not numbers:
        pad_digits = 0

    # Phase #1
    term = Lib.htmlToPlainText(term)
    term = delete_ignored_firsts(term, ignored)     # [10]
    parts = []
    precedence = None
    for i, word in enumerate(term.split()):
        word = word.casefold()                      # [1]
        word, hyphens = WORD_SEP_RX.subn("", word)  # [3]
        if not word:
            continue
        word = Normalize.unaccented(word)                # [2]
        # Must follow casefold & unaccented
        word = O_APOSTROPHE_RX.sub("o", word)    # [9]
        word = APOSTROPHE_S_RX.sub("s", word)    # [X1]
        theword = word.split()[0].rstrip()
        if i == 0: # First word
            if theword.endswith(","):
                precedence = "H"                    # [7]
            elif hyphens and word and word[-1].isdigit():
                precedence = "P"                    # [8]a
                match = FINAL_DIGITS_RX.search(word)
                if match is not None:
                    pos = match.start(1)
                    word = word[:pos] + " " + word[pos:]
        elif i == 1 and precedence is None: # Second word
            if theword.startswith("("):
                precedence = "D"                    # [6]
            elif theword:
                if theword[0].isdigit():
                    precedence = "P"                # [8]b
        word = NOT_LETTERS_OR_DIGITS_RX.sub(" ", word)      # [3]
        j = i
        for word in word.split():                   # [5]
            if i == 0 and spell_numbers: # First word only
                word = spelled_number(word, roman_numerals).replace(" ", "")
            elif pad_digits:
                word, done = padded_number(word, roman_numerals, pad_digits)
                if (done and j == 1 and
                        (precedence is None or precedence in "LT")):
                    precedence = "P"                # [8]c
            parts.append(word)
            j += 1
    if not parts:
        return ""

    # Phase #2
    words = [parts[0]]
    if precedence is not None:
        words.append(precedence)
    words += parts[1:]
    return "".join(words)


@registerRules
@functools.lru_cache(maxsize=None)
def wordByWordCMS16(term, saf=Saf.AUTO, *, pad_digits=DEFAULT_PAD_DIGITS,
                    ignored=None):
    """Word by Word (Chicago Manual of Style) «CMS by Word»

    Converts a term to a "sort as" text that when sorted "naturally"
    will give the word by word ordering specified in Chicago 16th
    edition 16.60.

    The captial letter that may appear between the first and second word
    is used to force the correct order of precedence.
    """
    # ignored should be None or an empty set for main entries, and a
    # set of articles, conjunctions, and prepositions to ignore for
    # subentries.
    #
    # Rules (all words):
    #     casefold                                  [1]
    #     strip accents                             [2]
    #     replace non-letters and non-digits with spaces [3]
    #     O'Name                -> oname            [11]
    # Rules (first word only):
    #     aword-bword         -> awordbword         [4]
    # Precedence (first word only):
    #     word                  -> word             [5]
    #     word (.*              -> word D .*        [6]
    #     word, .*              -> word H .*        [7]
    #     word .*               -> word L .*        [8]
    #     word\s*[,;:.]*\d+.*   -> word P \d+.*     [9]
    #     word\s+\l.*           -> word T \l.*      [10]
    # Subentries: remove leading articles,          [12]
    #   conjunctions, and prepositions.
    # Extensions:
    #     word's                -> words            [X1]

    numbers, roman_numerals, spell_numbers = Saf.flags(saf)
    if not numbers:
        pad_digits = 0

    # Phase #1
    term = Lib.htmlToPlainText(term)
    term = delete_ignored_firsts(term, ignored) # [12]
    parts = []
    precedence = None
    for i, word in enumerate(term.split()):
        word = word.casefold()                      # [1]
        if i == 0: # First word
            word = WORD_SEP_RX.sub("", word)   # [4]
        if not word:
            continue
        word = Normalize.unaccented(word)                # [2]
        # Must follow casefold & unaccented
        word = O_APOSTROPHE_RX.sub("o", word)    # [11]
        word = APOSTROPHE_S_RX.sub("s", word)    # [X1]
        theword = word.split()[0].rstrip()
        if i == 0: # First word
            if theword.endswith(","):
                precedence = "H"                    # [7]
        elif i == 1 and precedence is None: # Second word
            if theword.startswith("("):
                precedence = "D"                    # [6]
            elif theword:
                if theword[0].isdigit():
                    precedence = "P"                # [9]a
                elif theword[0].isalpha():
                    precedence = "L"                # [8]
            if precedence is None:
                precedence = "T"                    # [10]
        word = NOT_LETTERS_OR_DIGITS_RX.sub(" ", word)     # [3]
        j = i
        for word in word.split():                   # [5]
            if i == 0 and spell_numbers: # First word only
                word = spelled_number(word, roman_numerals)
            elif pad_digits:
                word, done = padded_number(word, roman_numerals, pad_digits)
                if (done and j == 1 and
                        (precedence is not None and precedence in "LT")):
                    precedence = "P"                # [9]b
            parts.append(word)
            j += 1
    if not parts:
        return ""

    # Phase #2
    words = [parts[0]]
    if precedence is not None:
        words.append(precedence)
    words += parts[1:]
    return " ".join(words)
