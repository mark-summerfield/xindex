#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import functools
import unicodedata


CHARS4LIGATURE = {
    "ﬀ": "ff",
    "ﬁ": "fi",
    "ﬂ": "fl",
    "ﬃ": "ffi",
    "ﬄ": "ffl",
    "ﬅ": "ſt",
    "ﬆ": "st",
    }

UNCOMPOUNDED4COMPOUNDED = {
    0x00C6: "AE",
    0x00DF: "fs",
    0x00E6: "ae",
    0x0132: "IJ",
    0x0133: "ij",
    0x0152: "OE",
    0x0153: "oe",
    0x01C4: "DZ",
    0x01C5: "Dz",
    0x01C6: "dz",
    0x01C7: "LJ",
    0x01C8: "Lj",
    0x01C9: "lj",
    0x01CA: "NJ",
    0x01CB: "Nj",
    0x01CC: "nj",
    0x01F1: "DZ",
    0x01F2: "Dz",
    0x01F3: "dz",
    0x1D6B: "ue",
    0xA728: "TZ",
    0xA729: "tz",
    0xA732: "AA",
    0xA733: "aa",
    0xA734: "AO",
    0xA735: "ao",
    0xA736: "AU",
    0xA737: "au",
    0xA738: "AV",
    0xA739: "av",
    0xA73C: "AY",
    0xA73D: "ay",
    0xAB50: "ui",
    0xFB00: "ff",
    0xFB01: "fi",
    0xFB02: "fl",
    0xFB03: "ffi",
    0xFB04: "ffl",
    0xFB05: "ft",
    0xFB06: "st",
    0x1F670: "et",
    "…": "...",
    }

WS4WS = {
    0x0093: "\u201C",  # “
    0x0094: "\u201D",  # ”
    0x0020: " ", # Space
    0x00A0: " ", # Space
    0x1680: " ", # Space
    0x2000: " ", # Space
    0x2001: " ", # Space
    0x2002: " ", # Space
    0x2003: " ", # Space
    0x2004: " ", # Space
    0x2005: " ", # Space
    0x2006: " ", # Space
    0x2007: " ", # Space
    0x2008: " ", # Space
    0x2009: " ", # Space
    0x200A: " ", # Space
    0x202F: " ", # Space
    0x205F: " ", # Space
    0x3000: " ", # Space
    }

HYPHEN4HYPHEN = {
    0x002D: "-",
    0x058A: "-",
    0x05BE: "-",
    0x1400: "-",
    0x1806: "-",
    0x2010: "-",
    0x2011: "-",
    0x2012: "-",
    0x2013: "-",
    0x2014: "-",
    0x2015: "-",
    0x2E17: "-",
    0x2E1A: "-",
    0x2E3A: "-",
    0x2E3B: "-",
    0x2E40: "-",
    0x301C: "-",
    0x3030: "-",
    0x30A0: "-",
    0xFE31: "-",
    0xFE32: "-",
    0xFE58: "-",
    0xFE63: "-",
    0xFF0D: "-",
    }

ENGLISH4OTHER = {
    # Latin
    "à": "a", "á": "a", "â": "a", "ã": "a", "ä": "a", "å": "a",
    "æ": "ae", "ç": "c", "è": "e", "é": "e", "ê": "e", "ë": "e",
    "ì": "i", "í": "i", "î": "i", "ï": "i", "ð": "d", "ñ": "n",
    "ò": "o", "ó": "o", "ô": "o", "õ": "o", "ö": "o", "ő": "o",
    "ø": "o", "ù": "u", "ú": "u", "û": "u", "ü": "u", "ű": "u",
    "ý": "y", "þ": "th", "ÿ": "y",
    "À": "A", "Á": "A", "Â": "A", "Ã": "A", "Ä": "A", "Å": "A",
    "Æ": "AE", "Ç": "C", "È": "E", "É": "E", "Ê": "E", "Ë": "E",
    "Ì": "I", "Í": "I", "Î": "I", "Ï": "I", "Ð": "D", "Ñ": "N",
    "Ò": "O", "Ó": "O", "Ô": "O", "Õ": "O", "Ö": "O", "Ő": "O",
    "Ø": "O", "Ù": "U", "Ú": "U", "Û": "U", "Ü": "U", "Ű": "U",
    "Ý": "Y", "Þ": "TH", "ß": "ss",

    # Greek
    "α": "a", "β": "b", "γ": "g", "δ": "d", "ε": "e", "ζ": "z",
    "η": "h", "θ": "8", "ι": "i", "κ": "k", "λ": "l", "μ": "m",
    "ν": "n", "ξ": "3", "ο": "o", "π": "p", "ρ": "r", "σ": "s",
    "τ": "t", "υ": "y", "φ": "f", "χ": "x", "ψ": "ps", "ω": "w",
    "ά": "a", "έ": "e", "ί": "i", "ό": "o", "ύ": "y", "ή": "h",
    "ώ": "w", "ς": "s", "ϊ": "i", "ΰ": "y", "ϋ": "y", "ΐ": "i",
    "Α": "A", "Β": "B", "Γ": "G", "Δ": "D", "Ε": "E", "Ζ": "Z",
    "Η": "H", "Θ": "8", "Ι": "I", "Κ": "K", "Λ": "L", "Μ": "M",
    "Ν": "N", "Ξ": "3", "Ο": "O", "Π": "P", "Ρ": "R", "Σ": "S",
    "Τ": "T", "Υ": "Y", "Φ": "F", "Χ": "X", "Ψ": "PS", "Ω": "W",
    "Ά": "A", "Έ": "E", "Ί": "I", "Ό": "O", "Ύ": "Y", "Ή": "H",
    "Ώ": "W", "Ϊ": "I", "Ϋ": "Y",

    # Turkish
    "ş": "s", "Ş": "S", "ı": "i", "İ": "I", "ç": "c", "Ç": "C",
    "ü": "u", "Ü": "U", "ö": "o", "Ö": "O", "ğ": "g", "Ğ": "G",

    # Russian
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e",
    "ё": "yo", "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k",
    "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "y", "ф": "f", "х": "h", "ц": "c",
    "ч": "ch", "ш": "sh", "щ": "sh", "ъ": "er", "ы": "y", "ь": "er",
    "э": "e", "ю": "y", "я": "ya",
    "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E",
    "Ё": "Yo", "Ж": "Zh", "З": "Z", "И": "I", "Й": "Y", "К": "K",
    "Л": "L", "М": "M", "Н": "N", "О": "O", "П": "P", "Р": "R",
    "С": "S", "Т": "T", "У": "U", "Ф": "F", "Х": "H", "Ц": "C",
    "Ч": "Ch", "Ш": "Sh", "Щ": "Sh", "Ъ": "er", "Ы": "Y", "Ь": "er",
    "Э": "E", "Ю": "Y", "Я": "Ya",

    # Ukrainian
    "Є": "Ye", "І": "I", "Ї": "Yi", "Ґ": "G",
    "є": "ye", "і": "i", "ї": "yi", "ґ": "g",

    # Czech
    "č": "c", "ď": "d", "ě": "e", "ň": "n", "ř": "r", "š": "s",
    "ť": "t", "ů": "u", "ž": "z",
    "Č": "C", "Ď": "D", "Ě": "E", "Ň": "N", "Ř": "R", "Š": "S",
    "Ť": "T", "Ů": "U", "Ž": "Z",

    # Polish
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o",
    "ś": "s", "ź": "z", "ż": "z",
    "Ą": "A", "Ć": "C", "Ę": "e", "Ł": "L", "Ń": "N", "Ó": "O",
    "Ś": "S", "Ź": "Z", "Ż": "Z",

    # Latvian
    "ā": "a", "č": "c", "ē": "e", "ģ": "g", "ī": "i", "ķ": "k",
    "ļ": "l", "ņ": "n", "š": "s", "ū": "u", "ž": "z",
    "Ā": "A", "Č": "C", "Ē": "E", "Ģ": "G", "Ī": "i", "Ķ": "k",
    "Ļ": "L", "Ņ": "N", "Š": "S", "Ū": "U", "Ž": "Z",

    # Kazakh
    "ә": "a", "ғ": "g", "қ": "k", "ң": "n", "ө": "o", "ұ": "u",
    "ү": "u", "һ": "h", "і": "i",
    "Ә": "A", "Ғ": "G", "Қ": "K", "Ң": "N", "Ө": "O", "Ұ": "U",
    "Ү": "U", "Һ": "H", "І": "I",
    }


BASE = CHARS4LIGATURE.copy()
BASE.update(UNCOMPOUNDED4COMPOUNDED)
BASE.update(ENGLISH4OTHER)

UNACCENTED = str.maketrans(BASE)

ALL = UNACCENTED.copy()
ALL.update(HYPHEN4HYPHEN)
ALL.update(WS4WS)

NORMALIZE = str.maketrans(ALL)


def _normalize(text, table=NORMALIZE):
    return nfc("".join(c for c in nfd(text.translate(table))
               if not unicodedata.combining(c)))


normalize = functools.partial(_normalize, table=NORMALIZE)


unaccented = functools.partial(_normalize, table=UNACCENTED)


nfc = functools.partial(unicodedata.normalize, "NFC")


nfd = functools.partial(unicodedata.normalize, "NFD")
