#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

CUSTOM = "c"
AUTO = "A" # All: numbers, roman, and spell
AUTO_NUMBER_ROMAN = "R"
AUTO_NUMBER_SPELL = "S"
AUTO_NUMBER = "N"
AUTO_BASIC = "B" # No numbers or roman

COMBINATIONS = (AUTO, AUTO_NUMBER_ROMAN, AUTO_NUMBER_SPELL, AUTO_NUMBER,
                AUTO_BASIC) # Order matters! See key() function, below.


def flags(saf):
    """Returns 3 bools: numbers, roman_numerals, spell_numbers"""
    if saf == AUTO:
        return True, True, True
    if saf == AUTO_NUMBER_ROMAN:
        return True, True, False
    if saf == AUTO_NUMBER_SPELL:
        return True, False, True
    if saf == AUTO_NUMBER:
        return True, False, False
    return False, False, False


def key(saf):
    if saf == AUTO:
        return 1
    if saf == AUTO_NUMBER_ROMAN:
        return 2
    if saf == AUTO_NUMBER_SPELL:
        return 3
    if saf == AUTO_NUMBER:
        return 4
    return 5
