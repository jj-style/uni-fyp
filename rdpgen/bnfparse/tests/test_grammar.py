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
    assert ls == {"i": "F", "(": "F"}

    ls = g.left_set("R")
    assert ls == {"+": "R", "#": "R"}

    ls = g.left_set("T")
    assert ls == {"i": "F", "(": "F"}

    ls = g.left_set("Y")
    assert ls == {"*": "Y", "#": "Y"}

    ls = g.left_set("F")
    assert ls == {"i": "F", "(": "F"}


def test_grammar_left_set_with_groups():
    g = Grammar.from_bnf(GRAMMAR_GROUPS)
    ls = g.left_set("A")
    assert ls == {"a": "A", "b": "B", "c": "C"}
    ls = g.left_set("B")
    assert ls == {"b": "B"}
    ls = g.left_set("C")
    assert ls == {"c": "C", "a": "A", "b": "B"}


def test_grammar_optionals():
    g = Grammar.from_bnf(GRAMMAR_OPTIONALS)
    ls = g.left_set("IF")
    assert ls == {"if": "IF"}
    ls = g.left_set("ELSE")
    assert ls == {"else": "ELSE"}


def test_grammar_optional_start():
    g = Grammar.from_bnf(GRAMMAR_OPTIONAL_START)
    ls = g.left_set("FACTOR")
    assert ls == {"0": "DIGIT", "1": "DIGIT", "2": "DIGIT", "3": "DIGIT"}
