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
    assert ls == {"i": "F", "(": "F"}

    ls = g.left_set("R")
    assert ls == {"+": "R", "#": "R"}

    ls = g.left_set("T")
    assert ls == {"i": "F", "(": "F"}

    ls = g.left_set("Y")
    assert ls == {"*": "Y", "#": "Y"}

    ls = g.left_set("F")
    assert ls == {"i": "F", "(": "F"}
