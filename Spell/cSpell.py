#!/usr/bin/env python3
# Copyright © 2014-20 Qtrac Ltd. All rights reserved.

import ctypes

import Lib
from Const import WIN, IS64BIT


class Error(Exception):
    pass


if WIN:
    if IS64BIT:
        HUNSPELL_DLL = Lib.get_path(r"Spell\spelling\libhunspell64.dll")
    else:
        HUNSPELL_DLL = Lib.get_path(r"Spell\spelling\libhunspell.dll")
else:
    HUNSPELL_DLL = "/usr/lib/x86_64-linux-gnu/libhunspell.so"
_hunspell = ctypes.cdll.LoadLibrary(HUNSPELL_DLL)
if _hunspell is None:
    raise Error("cannot find spelling library")

_hunspell.Hunspell_create.argtypes = (ctypes.c_char_p, ctypes.c_char_p)
_hunspell.Hunspell_create.restype = ctypes.POINTER(ctypes.c_int)

_hunspell.Hunspell_destroy.argtype = ctypes.POINTER(ctypes.c_int)
_hunspell.Hunspell_destroy.restype = None

_hunspell.Hunspell_spell.argtypes = (ctypes.POINTER(ctypes.c_int),
                                     ctypes.c_char_p)
_hunspell.Hunspell_spell.restype = ctypes.c_int

_hunspell.Hunspell_add.argtypes = (ctypes.POINTER(ctypes.c_int),
                                   ctypes.c_char_p)
_hunspell.Hunspell_add.restype = ctypes.c_int

_hunspell.Hunspell_remove.argtypes = (ctypes.POINTER(ctypes.c_int),
                                      ctypes.c_char_p)
_hunspell.Hunspell_remove.restype = ctypes.c_int

_hunspell.Hunspell_suggest.argtypes = (
    ctypes.POINTER(ctypes.c_int),
    ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p)),
    ctypes.c_char_p)
_hunspell.Hunspell_suggest.restype = ctypes.c_int
