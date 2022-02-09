GRAMMAR_BNF = """E ::= T R
R ::= "+" T R | "#"
T ::= F Y
Y ::= "*" F Y | "#"
F ::= "(" E ")" | "i"
"""

from ..parse import Grammar


def test_grammar_parse_bnf():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    assert len(g.productions) == 5


def test_grammar_left_set():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    ls = g.left_set("E")
    assert ls == set(["(", "i"])

    ls = g.left_set("R")
    assert ls == set(["+", "#"])

    ls = g.left_set("T")
    assert ls == set(["(", "i"])

    ls = g.left_set("Y")
    assert ls == set(["*", "#"])

    ls = g.left_set("F")
    assert ls == set(["(", "i"])
