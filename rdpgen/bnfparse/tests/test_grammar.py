GRAMMAR_BNF = """E ::= T R
R ::= "+" T R | "#"
T ::= F Y
Y ::= "*" F Y | "#"
F ::= "(" E ")" | "i"
"""

# MATH_GRAMMAR = """program ::= expression expression_star
# expression_star ::= expression expression_star | "¬"
# expression ::= arithmeticExpression arithmeticStar
# arithmeticStar ::= arithmeticOp arithmeticExpression | "¬"
# arithmeticOp ::= "=" | ">" | "<"
# arithmeticExpression ::= term termStar
# termStar ::= termOp term | "¬"
# termOp ::= "+" | "-"
# term ::= factor factorStar
# factorStar ::= factorOp factor | "¬"
# factorOp ::= "*" | "/"
# factor ::= minusOpt operand
# minusOpt ::= "-" | "¬"
# operand ::= <int> | <float> | <identifier>"""

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


# def test_math_grammar_left_set_with_epsilons():
#     g = Grammar.from_bnf(MATH_GRAMMAR)
#     ls = g.left_set("program")
#     print(ls)
#     assert ls == {
#         "-": {"parent": "minusOpt"},
#         "¬": {"parent": "minusOpt"},
#         "int": {"parent": "operand", "token": True},
#         "float": {"parent": "operand", "token": True},
#         "identifier": {"parent": "operand", "token": True},
#     }
#     assert False
