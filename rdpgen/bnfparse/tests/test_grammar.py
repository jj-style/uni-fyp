GRAMMAR_BNF = """E ::= T R
R ::= "+" T R | "#"
T ::= F Y
Y ::= "*" F Y | "#"
F ::= "(" E ")" | "i"
"""

MATH_GRAMMAR = """program ::= expression expression_star
expression_star ::= expression expression_star | "¬"
expression ::= arithmeticExpression arithmeticStar
arithmeticStar ::= arithmeticOp arithmeticExpression | "¬"
arithmeticOp ::= "=" | ">" | "<"
arithmeticExpression ::= term termStar
termStar ::= termOp term | "¬"
termOp ::= "+" | "-"
term ::= factor factorStar
factorStar ::= factorOp factor | "¬"
factorOp ::= "*" | "/"
factor ::= minusOpt operand
minusOpt ::= "-" | "¬"
operand ::= <int> | <float> | <identifier>"""

GRAMMAR_BNF_WITH_TOKENS = """ASSIGN ::= <IDENTIFIER> "=" <DIGIT>
"""

from ..parse import Grammar


def test_grammar_parse_bnf():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    assert len(g.productions) == 5


def test_grammar_left_set():
    g = Grammar.from_bnf(GRAMMAR_BNF)
    ls = g.left_set("E")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "i": {"parent": "F", "token": False},
        "(": {"parent": "F", "token": False},
    }

    ls = g.left_set("R")

    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "+": {"parent": "R", "token": False},
        "#": {"parent": "R", "token": False},
    }

    ls = g.left_set("T")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "i": {"parent": "F", "token": False},
        "(": {"parent": "F", "token": False},
    }

    ls = g.left_set("Y")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "*": {"parent": "Y", "token": False},
        "#": {"parent": "Y", "token": False},
    }

    ls = g.left_set("F")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "i": {"parent": "F", "token": False},
        "(": {"parent": "F", "token": False},
    }


def test_grammar_left_set_tokens():
    g = Grammar.from_bnf(GRAMMAR_BNF_WITH_TOKENS)
    ls = g.left_set("ASSIGN")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {"IDENTIFIER": {"parent": "ASSIGN", "token": True}}


def test_math_grammar_left_set_with_epsilons():
    g = Grammar.from_bnf(MATH_GRAMMAR)
    ls = g.left_set("program")
    for k in ls.keys():
        if "or_term" in ls[k]:
            ls[k].pop("or_term")
    assert ls == {
        "-": {"parent": "minusOpt", "token": False},
        "¬": {"parent": "minusOpt", "token": False},
        "int": {"parent": "operand", "token": True},
        "float": {"parent": "operand", "token": True},
        "identifier": {"parent": "operand", "token": True},
    }
