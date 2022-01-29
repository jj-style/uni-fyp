from enum import Enum, auto
from typing import Dict

""" EBNF grammar:
   expression ::= term ( "|" term )+
   term ::= factor suffix? (" " factor suffix?)+
   suffix ::= "?" | "+" | "*"
   factor ::= ("(" expression ")") | expression
   factor ::= RULE
"""


class NodeType(Enum):
    TERMINAL = auto()
    NONTERMINAL = auto()
    OPTIONAL = auto()
    ONE_OR_MORE = auto()
    ZERO_OR_MORE = auto()
    GROUP = auto()
    OR = auto()
    TERM = auto()


class Node:
    def __init__(self, node_type, value=None, *children):
        self._value = value
        self._type = node_type
        self._children = [c for c in children]

    def add_children(self, *children):
        for child in children:
            self._children.append(child)

    def __str__(self, level=0):
        "https://stackoverflow.com/a/20242504"
        ret = "\t" * level + repr(self) + "\n"
        for child in self._children:
            ret += child.__str__(level + 1)
        return ret

    def __repr__(self):
        return f"{self._type}{':' + self._value if self._value else ''}"


class Parser:
    def __init__(self, string: str):
        self.tokens = string.split(" ")
        self.tree = None

    @property
    def has_next(self):
        return len(self.tokens) > 0

    def peek(self):
        return self.tokens[0] if self.has_next else None

    def next(self):
        return self.tokens.pop(0) if self.has_next else None

    def parse(self):
        self.tree = self.expression()

    def expression(self):
        """expression ::= term ( "|" term )+"""
        node = self.term()
        while self.peek() == "|":
            old = node
            node = Node(NodeType.OR)
            self.next()  # consume "|"
            right = self.term()

            node.add_children(old, right)

        return node

    def term(self):
        old, right = None, None
        """term ::= factor suffix? (" " factor suffix?)+"""
        node = self.factor()
        if self.peek() in ["?", "+", "*"]:
            old = node
            node = Node(NodeType.TERM)
            right = self.suffix()
            node.add_children(old, right)

        while self.peek() not in ["|", ")", None]:  # TODO: confirm this is right
            left = node
            node = Node(NodeType.TERM)
            node.add_children(left)
            next_node = self.factor()
            if self.peek() in ["?", "+", "*"]:
                old = next_node
                next_node = Node(NodeType.TERM)
                right = self.suffix()
                next_node.add_children(old, right)
            node.add_children(next_node)

        return node

    def suffix(self):
        """suffix ::= "?" | "+" | "*" """
        n = self.next()
        if n in ["?", "+", "*"]:
            node_type = None
            if n == "?":
                node_type = NodeType.OPTIONAL
            elif n == "+":
                node_type = NodeType.ONE_OR_MORE
            elif n == "*":
                node_type = NodeType.ZERO_OR_MORE
            return Node(node_type)
        else:
            raise Exception(f"unknown suffix: {n}")

    def factor(self):
        """factor ::= "(" expression ")" """
        if self.peek() == "(":
            self.consume("(")
            grouped = self.expression()
            self.consume(")")
            return grouped  # Node(grouped, "grouped")
        else:
            value = self.next()
            node_type = NodeType.NONTERMINAL
            if value[0] == value[-1] and value[0] == '"':
                node_type = NodeType.TERMINAL
            return Node(node_type, value=value)

    def consume(self, expected: str):
        n = self.next()
        if n:
            if n == expected:
                return
            else:
                raise Exception(f"expected: '{expected}', got '{n}'")
        else:
            raise Exception(f"expected {expected}, got end of sequence")

    def print_tree(self):
        print(self.tree)


class Grammar:
    @staticmethod
    def bnf_from_grammar_dict(grammar_dict: Dict[str, str]) -> str:
        grammar_bnf = ""
        for rule, prod in grammar_dict.items():
            grammar_bnf += f"{rule} ::= {prod}" + "\n"
        return grammar_bnf

    @classmethod
    def from_bnf(cls):
        productions = {}
        for rule in rules.splitlines():
            name, rhs = rule.split(" ::= ")
            productions[name] = rhs
        return cls(productions)

    def __init__(self, rules: Dict[str, str]):
        self.__rules = rules
        self.productions = {}
        for name, production in rules.items():
            production_parser = Parser(production)
            production_parser.parse()
            self.productions[name] = production_parser.tree

    @property
    def bnf(self) -> str:
        return Grammar.bnf_from_grammar_dict(self.__rules)

    def __str__(self) -> str:
        return "\n".join(f"{k} ->\n{v}" for k, v in self.productions.items())


if __name__ == "__main__":
    # p = Parser("( x | y ) ? | z")
    # p = Parser('( x | y ) | "z" ?')
    # p = Parser("( x * y ) ? | z")

    rules = {"noun-phrase": "article noun", "article": '"the" | "a" | "an"'}
    g = Grammar(rules)
    print(g)
