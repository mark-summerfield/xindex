#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

"""
>>> from . import Spell
>>> Spell.check("blue")
True
>>> Spell.check("xxxxxxxxx")
False
>>> Spell.check("gorila")
False
>>> Spell.suggest("gorila")[:2]
['gorilla', 'gorily']
>>> Spell.add("XyZ")
True
>>> Spell.check("XyZ")
True
>>> Spell.remove("XyZ")
True
>>> Spell.check("XyZ")
False
"""

import atexit
import ctypes
import os

import Lib
from . import cSpell
from Const import LanguageKind, UTF8


_handleForLanguage = {}


def languages():
    return sorted(_handleForLanguage.keys())


def check(word, language=LanguageKind.AMERICAN.value):
    handle = _handleForLanguage[language]
    return bool(cSpell._hunspell.Hunspell_spell(handle, word.encode(UTF8)))


def suggest(word, language=LanguageKind.AMERICAN.value):
    handle = _handleForLanguage[language]
    a = ctypes.c_char_p()
    p = ctypes.pointer(a)
    pp = ctypes.pointer(p)
    count = cSpell._hunspell.Hunspell_suggest(handle, pp, word.encode(UTF8))
    p = pp.contents
    suggestions = []
    for i in range(count):
        suggestions.append(ctypes.c_char_p(p[i]).value.decode(UTF8,
                           errors="ignore"))
    cSpell._hunspell.Hunspell_free_list(handle, pp, count)
    return suggestions


def add(word, language=LanguageKind.AMERICAN.value):
    handle = _handleForLanguage[language]
    return not bool(cSpell._hunspell.Hunspell_add(handle,
                                                  word.encode(UTF8)))


def remove(word, language=LanguageKind.AMERICAN.value):
    handle = _handleForLanguage[language]
    return not bool(cSpell._hunspell.Hunspell_remove(handle,
                                                     word.encode(UTF8)))


def _add_dictionary(language, afffile, dicfile):
    handle = cSpell._hunspell.Hunspell_create(bytes(afffile, UTF8),
                                              bytes(dicfile, UTF8))
    _handleForLanguage[language] = handle


def _cleanup():
    for handle in _handleForLanguage.values():
        cSpell._hunspell.Hunspell_destroy(handle)
    _handleForLanguage.clear()


path = Lib.get_path("Spell/spelling")
for name in sorted(os.listdir(path)):
    if name.endswith(".dic"):
        language = os.path.splitext(name)[0]
        dic = os.path.join(path, language + ".dic")
        aff = os.path.join(path, language + ".aff")
        if os.path.exists(aff) and os.path.exists(dic):
            _add_dictionary(language, aff, dic)
del path, name


atexit.register(_cleanup)
