import re
from typing import List, Dict
from .parsergen import parser_from_grammar
from .core import Expression, Term, Factor, Grammar, Production, NodeType

RULE = re.compile(r"<(?P<name>.*)>\s*::=\s*(?P<expression>.*)")
NONTERMINAL = re.compile(r"<(.*)>")


def parse_expression(stream: List[str]) -> Expression:
    terms: List[Term] = []
    terms.append(parse_term(stream))
    while len(stream) > 0 and stream[0] == "|":
        stream.pop(0)
        terms.append(parse_term(stream))
    return Expression(terms)


def parse_term(stream: List[str]) -> List[Factor]:
    factors: List[Factor] = []
    factors.append(parse_factor(stream))
    while len(stream) > 0 and stream[0].isspace():
        stream.pop(0)
        factors.append(parse_factor(stream))
    return Term(factors)


def parse_factor(stream: List[str]):
    factor = stream.pop(0)
    nonterm_match = NONTERMINAL.match(factor)
    if nonterm_match:
        return Factor(NodeType.nonterminal, nonterm_match.group(1))
    return Factor(NodeType.terminal, factor)


def parse_bnf(rules: str) -> Grammar:
    """hand-hacked BNF parser

    Args:
        rules (str): BNF grammar rules
    """
    productions = []
    for rule in [x for x in rules.split("\n") if x]:
        matches = RULE.match(rule).groupdict()
        # hand-hacked lexing of BNF rules
        expression = []
        chars = [c for c in matches["expression"]]
        while len(chars) > 0:
            current_token = chars.pop(0)
            if current_token.isspace():
                while chars[0].isspace():
                    current_token += chars.pop(0)
                if chars[0] == "|":
                    current_token = chars.pop(0)
                    while chars[0].isspace():
                        chars.pop(0)
            else:
                while len(chars) > 0 and not chars[0].isspace():
                    current_token += chars.pop(0)
            expression.append(current_token)
        # parse the lexed BNF
        tree = parse_expression(expression)
        p = Production(matches["name"], tree)
        productions.append(p)
    return Grammar(productions)


def bnf_from_grammar_config(grammar_config: Dict[str, str]) -> str:
    grammar_bnf = ""
    for rule, prod in grammar_config.items():
        grammar_bnf += f"<{rule}> ::= {prod}" + "\n"
    return grammar_bnf


if __name__ == "__main__":
    with open("test.bnf", "r") as f:
        contents = f.read()
    grammar = parse_bnf(contents)
    parser_from_grammar(grammar)
