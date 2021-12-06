""" EBNF grammar:
   expression ::= term ( "|" term )+
   term ::= factor suffix?
   suffix ::= "?" | "+" | "*"
   factor ::= ("(" expression ")") | expression
   factor ::= RULE
"""

from enum import Enum, auto


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
    def __init__(self, node_type, value=None, left=None, right=None):
        self._value = value
        self._type = node_type
        self._left = left
        self._right = right

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, value):
        self._left = value

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, value):
        self._right = value

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
        left = self.term()
        while self.peek() == "|":
            node = Node(NodeType.OR)
            self.next()  # consume "|"
            right = self.term()

            node.left = left
            node.right = right
            left = node
        return left

    def term(self):
        """term ::= factor suffix?"""
        left = self.factor()
        if self.peek() in ["?", "+", "*"]:
            node = Node(NodeType.TERM)
            right = self.suffix()

            # make sure suffix is left of node
            node.left = right
            node.right = left
            left = node
        return left

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
        self.__print_tree(self.tree)

    def __print_tree(self, node, level=0):
        "https://stackoverflow.com/a/62856494"
        if node is not None:
            self.__print_tree(node.left, level + 1)
            print(" " * 8 * level + "->", node)
            self.__print_tree(node.right, level + 1)


if __name__ == "__main__":
    # p = Parser("( x | y ) ? | z")
    # p = Parser('( x | y ) | "z" ?')
    p = Parser("x y | z")
    try:
        p.parse()
        p.print_tree()
        print(p.tree.left)
        print(p.tree.right)
    except Exception as e:
        print(e)
