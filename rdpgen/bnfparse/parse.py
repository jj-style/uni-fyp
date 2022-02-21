from enum import Enum, auto
from typing import Dict, List
from copy import deepcopy

""" EBNF grammar:
   expression ::= term ( "|" term )+
   term ::= factor  (" " factor )+
   factor ::=  expression
   factor ::= RULE
"""


class NodeType(Enum):
    TERMINAL = auto()
    NONTERMINAL = auto()
    TOKEN = auto()
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

    def __eq__(self, other):
        if isinstance(other, NodeType):
            return self._type == other
        return False

    @property
    def children(self):
        return self._children

    @property
    def value(self):
        return self._value


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
            if node != NodeType.OR:
                old = node
                node = Node(NodeType.OR)
                node.add_children(old)
            self.next()  # consume "|"
            right = self.term()
            node.add_children(right)

        return node

    def term(self):
        """term ::= factor  (" " factor )+"""
        node = self.factor()

        while self.peek() not in ["|", None]:  # TODO: confirm this is right
            if node != NodeType.TERM:
                old = node
                node = Node(NodeType.TERM)
                node.add_children(old)
            next_node = self.factor()
            node.add_children(next_node)

        return node

    def factor(self):
        value = self.next()
        node_type = NodeType.NONTERMINAL
        if value[0] == value[-1] and value[0] == '"':
            node_type = NodeType.TERMINAL
            value = value[1 : len(value) - 1]  # noqa
        elif value[0] == "<" and value[-1] == ">":
            node_type = NodeType.TOKEN
            value = value[1 : len(value) - 1]  # noqa
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
    def from_bnf(cls, rules):
        productions = {}
        for rule in rules.splitlines():
            name, rhs = rule.split(" ::= ")
            productions[name] = rhs
        return cls(productions)

    def __init__(self, rules: Dict[str, str]):
        self.__rules = rules
        self.productions = {}
        self.__start = None
        for name, production in rules.items():
            production_parser = Parser(production)
            production_parser.parse()
            self.productions[name] = production_parser.tree
        self.__start = list(rules.keys())[0]

    def bnf_from_rule(self, rule: str) -> str:
        return f"{rule} ::= {self.__rules[rule]}"

    @property
    def bnf(self) -> str:
        return Grammar.bnf_from_grammar_dict(self.__rules)

    def __str__(self) -> str:
        return "\n".join(f"{k} ->\n{v}" for k, v in self.productions.items())

    def __left_set_old(
        self,
        node: Node,
        terminals: Dict[str, List[str]],
        completed: List[Node],
        parent: Node,
    ) -> Dict[str, str]:
        if node in completed:
            # prevent infinite recursion by computing possible terminals
            # from node we've already computed and added to the terminal set
            return terminals
        if node not in completed:
            completed.append(node)

        terminals = deepcopy(terminals)

        if node == NodeType.TERM:
            for child in node.children:
                new_terminals = self.__left_set(child, terminals, completed, parent)
                if new_terminals != terminals:
                    terminals = new_terminals
                    break

        elif node == NodeType.OR:
            for child in node.children:
                terminals = self.__left_set(child, terminals, completed, parent)

        elif node == NodeType.TERMINAL:
            terminals[node.value] = {"parent": parent.value}

        elif node == NodeType.TOKEN:
            terminals[node.value] = {"parent": parent.value, "token": True}

        elif node == NodeType.NONTERMINAL:
            new_start = self.productions.get(node.value)
            terminals = self.__left_set(new_start, terminals, completed, node)
        return terminals

    def __left_set(
        self, node: Node, parent: Node, completed, terminals
    ) -> Dict[str, str]:
        completed.append(node)
        terminals = deepcopy(terminals)

        if node == NodeType.TERMINAL or node == NodeType.TOKEN:
            return {
                **terminals,
                node.value: {"parent": parent.value, "token": node == NodeType.TOKEN},
            }

        if node == NodeType.NONTERMINAL:
            next_node = self.productions.get(node.value)
            if next_node not in completed:
                nt_ls = self.__left_set(
                    self.productions.get(node.value), node, completed, terminals
                )
                terminals = {**terminals, **nt_ls}
            return terminals

        if node == NodeType.TERM:
            i = 0
            ls = {}
            next_ls = {}
            next_has_epsilon = True
            while i < len(node.children) and next_has_epsilon:
                next_has_epsilon = False
                if node.children[i] not in completed:
                    next_ls = self.__left_set(node.children[i], parent, completed, ls)
                    if "¬" in next_ls and "¬" not in ls:
                        next_has_epsilon = True
                    ls = {**ls, **next_ls}
                i += 1
            return {**terminals, **ls}

        if node == NodeType.OR:
            ls = {}
            for term in node.children:
                if term not in completed:
                    t_ls = self.__left_set(term, parent, completed, ls)
                    ls = {**ls, **t_ls}
            return {**terminals, **ls}

    def left_set(self, rule):
        start = self.productions.get(rule, None)
        if start is None:
            raise ValueError(f"{rule} is not a production in the grammar")

        return self.__left_set(start, Node(NodeType.NONTERMINAL, value=rule), [], {})

    def left_set_old(self, rule: str) -> Dict[str, str]:
        """Compute the left set of a grammar rule, returning a set of
        all possible terminals that we can expect to see
        """
        start = self.productions.get(rule, None)
        if start is None:
            raise ValueError(f"{rule} is not a production in the grammar")

        return self.__left_set_old(
            start, {}, [], Node(NodeType.NONTERMINAL, value=rule)
        )

    @property
    def start(self) -> str:
        return self.__start
