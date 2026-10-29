# -*- coding: utf-8 -*-
"""Прогон наброска спецификации: pip install maude; python3 run_spec.py"""
import os
import maude
maude.init(advise=False)
maude.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "gtrn_map.maude"))
m = maude.getModule("GTRN-MAP")
CASES = [
    "pop(1, 7, pop(1, 6, pop(1, 5, fm(pm(1, 0, 42, 0, none), 2, 3, 2))))",
    "pop(1, 9, pop(1, 8, pop(1, 7, pop(1, 6, pop(1, 5, "
    "fm(pm(1, 0, 42, 0, none), 2, 1, 2))))))",
    "born-here(pm(1, 0, 42, 2, rec(tn(1, 1), 5) rec(tn(1, 2), 6)) ; "
    "pm(2, 1, 42, 1, rec(tn(2, 1), 7)))",
]
for s in CASES:
    t = m.parseTerm(s)
    t.reduce()
    print(t.getSort(), "|", t)
