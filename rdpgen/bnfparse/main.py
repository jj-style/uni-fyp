import re
from enum import Enum
from typing import List
from pprint import pprint
RULE = re.compile(r'<(?P<name>.*)>\s*::=\s*(?P<expression>.*)')
NONTERMINAL = re.compile(r'<(.*)>')

class NodeType(Enum):
    terminal = 1
    nonterminal = 2

class Factor:
    def __init__(self, node_type: NodeType, name: str):
        self.node_type: NodeType = node_type
        self.name: str = name

    def __repr__(self):
        return f"Factor<node_type={self.node_type}, name={self.name}>"

class Term:
    def __init__(self, factors: List[Factor]):
        self.factors: List[Factor] = factors

    def __repr__(self):
        return f"Term<factors={f for f in self.factors}>"

class Production:
    def __init__(self, name, expression: List[Term]):
        self.name = name
        self.expression: List[Term] = expression

    def __repr__(self):
        return f"Production<name={self.name}, terms={list(t for t in self.expression)}>"

    # TODO
    def left_left(self) -> List[str]:
        raise NotImplementedError("compute the left set of a production rule -> derive possible set of initial terminals")

def parse_expression(stream: List[str]) -> List[Term]:
    terms: List[Term] = []
    terms.append(parse_term(stream))
    while len(stream) > 0 and stream[0] == "|":
        stream.pop(0)
        terms.append(parse_term(stream))
    return terms

def parse_term(stream: List[str]) -> List[Factor]:
    factors: List[Factor] = []
    factors.append(parse_factor(stream))
    while len(stream) > 0 and stream[0].isspace():
        stream.pop(0)
        factors.append(parse_factor(stream))
    return factors

def parse_factor(stream: List[str]):
    factor = stream.pop(0)
    nonterm_match = NONTERMINAL.match(factor)
    if nonterm_match:
        return Factor(NodeType.nonterminal, nonterm_match.group(1))
    return Factor(NodeType.terminal, factor)

def parse_bnf(rules: str) -> List[Production]:
    """hand-hacked BNF parser

    Args:
        rules (str): BNF grammar rules
    """
    productions = []
    for rule in rules.split("\n"):
        matches = RULE.match(rule).groupdict()
        expression = matches["expression"].split(" ")
        tree = parse_expression(expression)
        p = Production(matches["name"], tree)
        productions.append(p)
    return productions

def parser_from_productions(productions: List[Production]):
    for p in productions:
        # create function with p.name
        print(f"def parse_{p.name}():")
        print("\ttoken = get_token()")
        for idx,term in enumerate(p.expression):
            # get_token - check equals a term
            print(f"\t{'el' if idx > 0 else ''}", end="")
            print("if " + f"token == {term}:\n\t\tpass")
        print("\telse:\n\t\traise Exception()")                

if __name__ == "__main__":
    with open("test.bnf", "r") as f:
        contents = f.read()
    productions = parse_bnf(contents)
    parser_from_productions(productions)

