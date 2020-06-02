#!/usr/bin/env python3
# Copyright © 2015-20 Qtrac Ltd. All rights reserved.

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import unittest

import Normalize
import Saf
import SortAs
from Forms.SortAs import Candidate, humanizedCandidate
from Const import CandidateKind


class TestNormalize(unittest.TestCase):

    def test_Normalize(self):
        for i, phrase in enumerate(PHRASES):
            self.assertEqual(Normalize.normalize(phrase), EXPECTED[i])


    def test_humanizedCandidateCMS16(self):
        for i, (term, expected) in enumerate(CMS_DATA):
            with self.subTest(i=i):
                candidates = SortAs.candidatesFor(term, "wordByWordCMS16",
                                                  frozenset())
                actual = set()
                for candidate in candidates:
                    actual.add(humanizedCandidate(
                        term, candidate.candidate, candidate.saf))
                if actual != expected:
                    print("\nEXP\n  ",
                          "\n  ".join(str(x) for x in sorted(expected)),
                          sep="")
                    print("GOT\n  ",
                          "\n  ".join(str(x) for x in sorted(actual)),
                          sep="")
                self.assertSetEqual(expected, actual)


    def test_humanizedCandidateNISO(self):
        for i, (term, expected) in enumerate(NISO_DATA):
            with self.subTest(i=i):
                candidates = SortAs.candidatesFor(term, "wordByWordNISO3",
                                                  frozenset())
                actual = set()
                for candidate in candidates:
                    actual.add(humanizedCandidate(
                        term, candidate.candidate, candidate.saf))
                if actual != expected:
                    print("\nEXP\n  ",
                          "\n  ".join(str(x) for x in sorted(expected)),
                          sep="")
                    print("GOT\n  ",
                          "\n  ".join(str(x) for x in sorted(actual)),
                          sep="")
                self.assertSetEqual(expected, actual)



PHRASES = """\
——on, Nicholas
5000 años de historia
5.000 kilomètres dans le sud
Aastrøm, Jeppe
Aav, Yrjö
…and so to bed (ellipsis)
Åström, Margit
B … ch, A. (ellipsis)
Balzac, Honoré de
Müller, Fritz
Örne, Anders
Ørsted, Hans Christian
Peña, Carmen
Słonimski, Jan
Słownik geodezyjny
Ste. Geneviève
New, Zoë
ﬁles and shuﬄes
The Ænid œvre
""".split("\n")

EXPECTED = """\
--on, Nicholas
5000 anos de historia
5.000 kilometres dans le sud
Aastrom, Jeppe
Aav, Yrjo
...and so to bed (ellipsis)
Astrom, Margit
B ... ch, A. (ellipsis)
Balzac, Honore de
Muller, Fritz
Orne, Anders
Orsted, Hans Christian
Pena, Carmen
Slonimski, Jan
Slownik geodezyjny
Ste. Genevieve
New, Zoe
files and shuffles
The AEnid oevre
""".split("\n")

CMS_DATA = (
    ("Mr O'Brien's car, it's bad", set([
        Candidate(candidate='mr L obriens car its bad', term_word='Mr',
                  candidate_word='mr', kind=CandidateKind.UNCHANGED,
                  saf=Saf.AUTO)
        ])),
    ("It's at least 99", set([
        Candidate(candidate='its L at least 0099', term_word='99',
                  candidate_word='0099', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='its L at least 99', term_word='99',
                  candidate_word='99', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("Count to 100", set([
        Candidate(candidate='count L to 0100', term_word='100',
                  candidate_word='0100', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='count L to 100', term_word='100',
                  candidate_word='100', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("VI Warshawski", set([
        Candidate(candidate='six L warshawski', term_word='VI',
                  candidate_word='six', kind=CandidateKind.PHRASE,
                  saf=Saf.AUTO),
        Candidate(candidate='0006 L warshawski', term_word='VI',
                  candidate_word='0006', kind=CandidateKind.ROMAN,
                  saf=Saf.AUTO_NUMBER_ROMAN),
        Candidate(candidate='vi L warshawski', term_word='VI',
                  candidate_word='vi', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("Henry IV", set([
        Candidate(candidate='henry P 0004', term_word='IV',
                  candidate_word='0004', kind=CandidateKind.ROMAN,
                  saf=Saf.AUTO),
        Candidate(candidate='henry L iv', term_word='IV',
                  candidate_word='iv', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("C language", set([
        Candidate(candidate='one hundred L language',
                  term_word='C', candidate_word='one hundred',
                  kind=CandidateKind.PHRASE, saf=Saf.AUTO),
        Candidate(candidate='0100 L language',
                  term_word='C', candidate_word='0100',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO_NUMBER_ROMAN),
        Candidate(candidate='c L language', term_word='C',
                  candidate_word='c', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("C programming language", set([
        Candidate(candidate='one hundred L programming language',
                  term_word='C', candidate_word='one hundred',
                  kind=CandidateKind.PHRASE, saf=Saf.AUTO),
        Candidate(candidate='0100 L programming language',
                  term_word='C', candidate_word='0100',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO_NUMBER_ROMAN),
        Candidate(candidate='c L programming language', term_word='C',
                  candidate_word='c', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("The C programming language", set([
        Candidate(candidate='the P 0100 programming language',
                  term_word='C', candidate_word='0100',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO),
        Candidate(candidate='the L c programming language',
                  term_word='C', candidate_word='c',
                  kind=CandidateKind.LITERAL, saf=Saf.AUTO_NUMBER_SPELL),
        ])),
    ("A4 paper", set([
        Candidate(candidate='a4 L paper', term_word='A4',
                  candidate_word='a4', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO),
        Candidate(candidate='a0004 L paper', term_word='A4',
                  candidate_word='a0004', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO_NUMBER_ROMAN)
        ])),
    ("Albert's A5 paper", set([
        Candidate(candidate='alberts P a0005 paper', term_word='A5',
                  candidate_word='a0005', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='alberts L a5 paper', term_word='A5',
                  candidate_word='a5', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("10 green bottles", set([
        Candidate(candidate='ten L green bottles', term_word='10',
                  candidate_word='ten', kind=CandidateKind.PHRASE,
                  saf=Saf.AUTO),
        Candidate(candidate='0010 L green bottles', term_word='10',
                  candidate_word='0010', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO_NUMBER_ROMAN),
        Candidate(candidate='10 L green bottles', term_word='10',
                  candidate_word='10', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("a1 major", set([
        Candidate(candidate='a1 L major', term_word='a1',
                  candidate_word='a1', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO),
        Candidate(candidate='a0001 L major', term_word='a1',
                  candidate_word='a0001', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO_NUMBER_ROMAN)
        ])),
    ("Section 1.2", set([
        Candidate(candidate='section P 0001 0002', term_word='1.2',
                  candidate_word='0001', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='section P 1 2', term_word='1.2',
                  candidate_word='1', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("Section 2.4.6", set([
        Candidate(candidate='section P 0002 0004 0006', term_word='2.4.6',
                  candidate_word='0002', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='section P 2 4 6', term_word='2.4.6',
                  candidate_word='2', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO_BASIC)
        ])),
    )

NISO_DATA = (
    ("Mr O'Brien's car, it's bad", set([
        Candidate(candidate='mr obriens car its bad', term_word='Mr',
                  candidate_word='mr', kind=CandidateKind.UNCHANGED,
                  saf=Saf.AUTO)
        ])),
    ("It's at least 99", set([
        Candidate(candidate='its at least 0099.0000', term_word='99',
                  candidate_word='0099.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='its at least 99', term_word='99',
                  candidate_word='99', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("Count to 100", set([
        Candidate(candidate='count to 0100.0000', term_word='100',
                  candidate_word='0100.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='count to 100', term_word='100',
                  candidate_word='100', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("VI Warshawski", set([
        Candidate(candidate='0006.0000 warshawski', term_word='VI',
                  candidate_word='0006.0000', kind=CandidateKind.ROMAN,
                  saf=Saf.AUTO),
        Candidate(candidate='vi warshawski', term_word='VI',
                  candidate_word='vi', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("Henry IV", set([
        Candidate(candidate='henry 0004.0000', term_word='IV',
                  candidate_word='0004.0000', kind=CandidateKind.ROMAN,
                  saf=Saf.AUTO),
        Candidate(candidate='henry iv', term_word='IV',
                  candidate_word='iv', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("C language", set([
        Candidate(candidate='0100.0000 language',
                  term_word='C', candidate_word='0100.0000',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO),
        Candidate(candidate='c language', term_word='C',
                  candidate_word='c', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("C programming language", set([
        Candidate(candidate='0100.0000 programming language',
                  term_word='C', candidate_word='0100.0000',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO),
        Candidate(candidate='c programming language', term_word='C',
                  candidate_word='c', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_NUMBER_SPELL)
        ])),
    ("The C programming language", set([
        Candidate(candidate='the 0100.0000 programming language',
                  term_word='C', candidate_word='0100.0000',
                  kind=CandidateKind.ROMAN, saf=Saf.AUTO),
        Candidate(candidate='the c programming language',
                  term_word='C', candidate_word='c',
                  kind=CandidateKind.LITERAL, saf=Saf.AUTO_NUMBER_SPELL),
        ])),
    ("A4 paper", set([
        Candidate(candidate='a4 paper', term_word='A4',
                  candidate_word='a4', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC),
        Candidate(candidate='a0004.0000 paper', term_word='A4',
                  candidate_word='a0004.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO)
        ])),
    ("Albert's A5 paper", set([
        Candidate(candidate='alberts a0005.0000 paper', term_word='A5',
                  candidate_word='a0005.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='alberts a5 paper', term_word='A5',
                  candidate_word='a5', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("10 green bottles", set([
        Candidate(candidate='0010.0000 green bottles', term_word='10',
                  candidate_word='0010.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='10 green bottles', term_word='10',
                  candidate_word='10', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("a1 major", set([
        Candidate(candidate='a1 major', term_word='a1',
                  candidate_word='a1', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC),
        Candidate(candidate='a0001.0000 major', term_word='a1',
                  candidate_word='a0001.0000', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO)
        ])),
    ("Section 1.2", set([
        Candidate(candidate='section 0001.0002', term_word='1.2',
                  candidate_word='0001.0002', kind=CandidateKind.NUMBER,
                  saf=Saf.AUTO),
        Candidate(candidate='section 12', term_word='1.2',
                  candidate_word='12', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    ("Section 2.4.6", set([
        Candidate(candidate='section 000200040006.0000', term_word='2.4.6',
                  candidate_word='000200040006.0000',
                  kind=CandidateKind.NUMBER, saf=Saf.AUTO),
        Candidate(candidate='section 246', term_word='2.4.6',
                  candidate_word='246', kind=CandidateKind.LITERAL,
                  saf=Saf.AUTO_BASIC)
        ])),
    )

if __name__ == "__main__":
    unittest.main()
