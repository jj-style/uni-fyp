from enum import Enum
from typing import List, Set


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
        return f"Term<factors={self.factors}>"


class Expression:
    def __init__(self, terms: List[Term]):
        self.terms: List[Term] = terms

    def __repr__(self):
        return f"Expression<terms={self.terms}>"


class Production:
    def __init__(self, name, expression: Expression):
        self.name = name
        self.expression: Expression = expression

    def __repr__(self):
        return f"Production<name={self.name}, expression={self.expression}>"

    # TODO
    def left_set(self) -> Set[str]:
        raise NotImplementedError(
            "compute the left set of a production rule ->\
            derive possible set of initial terminals"
        )


class Grammar:
    def __init__(self, productions: List[Production]):
        self.productions = productions

    def __repr__(self):
        return f"Grammar<productions={self.productions}>"
