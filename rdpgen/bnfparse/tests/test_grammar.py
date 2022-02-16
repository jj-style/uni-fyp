GRAMMAR_BNF = """E ::= T R
R ::= "+" T R | "#"
T ::= F Y
Y ::= "*" F Y | "#"
F ::= "(" E ")" | "i"
"""

GRAMMAR_BNF_WITH_TOKENS = """ASSIGN ::= <IDENTIFIER> "=" <DIGIT>
"""

from ..parse import Grammar


def test_grammar_parse_bnf():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    assert len(g.productions) == 5


def test_grammar_left_set():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    ls = g.left_set("E")
    assert ls == {"i": {"parent": "F"}, "(": {"parent": "F"}}

    ls = g.left_set("R")
    assert ls == {"+": {"parent": "R"}, "#": {"parent": "R"}}

    ls = g.left_set("T")
    assert ls == {"i": {"parent": "F"}, "(": {"parent": "F"}}

    ls = g.left_set("Y")
    assert ls == {"*": {"parent": "Y"}, "#": {"parent": "Y"}}

    ls = g.left_set("F")
    assert ls == {"i": {"parent": "F"}, "(": {"parent": "F"}}


def test_grammar_left_set_tokens():
    g = Grammar.from_bnf(GRAMMAR_BNF_WITH_TOKENS)
    ls = g.left_set("ASSIGN")
    assert ls == {"IDENTIFIER": {"parent": "ASSIGN", "token": True}}
