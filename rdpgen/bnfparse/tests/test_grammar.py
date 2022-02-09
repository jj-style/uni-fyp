GRAMMAR_BNF = """E ::= T R
R ::= "+" T R | "#"
T ::= F Y
Y ::= "*" F Y | "#"
F ::= "(" E ")" | "i"
"""

GRAMMAR_GROUPS = """A ::= ( B | C ) | "a"
B ::= "b"
C ::= "c" | A
"""

GRAMMAR_OPTIONALS = """IF ::= "if" ID ELSE ?
ID ::= "x" | "y" | "z"
ELSE ::= "else"
"""

GRAMMAR_OPTIONAL_START = """FACTOR ::= "-" ? DIGIT
DIGIT ::= "0" | "1" | "2" | "3"
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


def test_grammar_left_set_with_groups():
    g = Grammar.from_bnf(GRAMMAR_GROUPS)
    ls = g.left_set("A")
    assert ls == set(["b", "c", "a"])
    ls = g.left_set("B")
    assert ls == set(["b"])
    ls = g.left_set("C")
    assert ls == set(["c", "a", "b"])


def test_grammar_optionals():
    g = Grammar.from_bnf(GRAMMAR_OPTIONALS)
    ls = g.left_set("IF")
    assert ls == set(["if"])
    ls = g.left_set("ELSE")
    assert ls == set(["else"])


def test_grammar_optional_start():
    g = Grammar.from_bnf(GRAMMAR_OPTIONAL_START)
    ls = g.left_set("FACTOR")
    assert ls == set(["0", "1", "2", "3"])
