from parse import parse_bnf, NodeType

RULES = """<sentence> ::= <noun-phrase> <predicate>
<noun-phrase> ::= <article> <noun>
<article> ::= the | a | an
<noun> ::= cat | flower
<predicate> ::= jumps | blooms"""


def test_parse_bnf():
    productions = parse_bnf(RULES).productions
    assert len(productions) == 5

    sentence = productions[0]
    assert sentence.name == "sentence"
    assert len(sentence.expression.terms[0].factors) == 2
    assert sentence.expression.terms[0].factors[0].name == "noun-phrase"
    assert sentence.expression.terms[0].factors[0].node_type == NodeType.nonterminal
    assert sentence.expression.terms[0].factors[1].name == "predicate"
    assert sentence.expression.terms[0].factors[1].node_type == NodeType.nonterminal

    article = productions[2]
    assert article.name == "article"
    assert len(article.expression.terms) == 3
    expected_factors = ["the", "a", "an"]
    for i in range(3):
        assert len(article.expression.terms[i].factors) == 1
        assert article.expression.terms[i].factors[0].node_type == NodeType.terminal
        assert article.expression.terms[i].factors[0].name == expected_factors[i]
