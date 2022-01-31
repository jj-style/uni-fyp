from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Union, Dict, List, Optional, Any, TypeVar
import os


class Primitive(Enum):
    Int = auto()
    Float = auto()
    String = auto()


class Composite:
    class CType(Enum):
        Array = auto()

    def __init__(self, base: CType, sub):
        self.base = base
        self.sub = sub

    def __repr__(self):
        return f"{self.base}<{self.sub}>"

    @classmethod
    def array(cls, t):
        return cls(Composite.CType.Array, t)


Type = TypeVar("Type", Primitive, Composite)


def imports(*packages):
    def import_wrapper(func):
        def wrap(self, *args, **kwargs):
            for pkg in packages:
                self.import_package(pkg)
            return func(self, *args, **kwargs)

        return wrap

    return import_wrapper


def expression(func):
    def wrap(*args, **kwargs):
        def lazy():
            return func(*args, **kwargs)

        return Expression(lazy)

    return wrap


class Expression:
    def __init__(self, expr_func):
        self.__f = expr_func

    def __str__(self):
        return self.__f()

    def __eq__(self, o):
        if type(o) is str:
            return str(self) == o
        return False


class Context:
    """Context for language"""

    def __init__(self, expand_tabs: bool = False, tab_size: int = 2):
        self.indent_lvl: int = 0
        self.expand_tabs: bool = expand_tabs
        self.tab_size: int = tab_size


class Language(ABC):
    def __init__(self, ctx: Context = None):
        self.imports = set()
        self.ctx = Context() if not ctx else ctx

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the language"""
        raise NotImplementedError

    @property
    def terminator(self) -> str:
        """Statement terminator"""
        return ""

    @property
    def whitespace_char(self) -> str:
        return " " * self.ctx.tab_size if self.ctx.expand_tabs else "\t"

    @property
    def linesep(self) -> str:
        return os.linesep

    def indent(self, stmt: str) -> str:
        return (self.ctx.indent_lvl * self.whitespace_char) + str(stmt)

    def import_package(self, pkg: str):
        """Adds a package to the list of imports

        Args:
            pkg (str): name of package/module
        """
        self.imports.add(pkg)

    def prelude(self, **kwargs) -> str:
        """Program can generate a prelude before the code, e.g. to add imports"""
        return ""

    @abstractmethod
    def types(self, t: Type) -> str:
        """How a language represents a type"""
        raise NotImplementedError

    @abstractmethod
    def string(self, s: str):
        """Construct a string in a language

        Args:
            s (str): the string to construct
        """
        raise NotImplementedError

    @abstractmethod
    def array(self, t: Type, elements: List[Any]):
        """Create an array in a language

        Args:
            t (Type): The type of elements contained in the array
            elements (List[Any]): elements to construct the array with
        """
        raise NotImplementedError

    @abstractmethod
    def declare(self, id: str, type: Type):
        """Declare a variable

        Args:
            id (str): identifier of the variable to declare
            type (Type): the type of the variable
        """
        raise NotImplementedError

    @abstractmethod
    def assign(self, id: str, expr):
        """Assign the result of an expression to an variable

        Args:
            id (str): identifier of the variable to assign to
            expr (Expression): the expression to evaluate
        """
        raise NotImplementedError

    @abstractmethod
    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type], None],
        *statements,
    ):
        # TODO - add documentation
        raise NotImplementedError

    @abstractmethod
    def block(self, *statements):
        """Block concept in a language,
        defining a scope and indentation for statements
        """
        raise NotImplementedError

    @abstractmethod
    def comment(self, comment: str):
        """Insert a comment in the language"""
        raise NotImplementedError

    @abstractmethod
    def do_return(self, expression=None):
        """Return from a function, with an optional expression to return"""
        raise NotImplementedError

    @abstractmethod
    def println(self, *args) -> str:
        """Prints values to stdout with a newline at the end"""
        raise NotImplementedError

    @abstractmethod
    def print(self, *args) -> str:
        """Prints values to stdout"""
        raise NotImplementedError

    @abstractmethod
    def for_loop(
        self,
        it: str,
        start: Expression,
        stop: Expression,
        step: Expression,
        *statements,
    ):
        """For loop implementation for a language.
        Arguments:
            it - loop iterator variable
            start - expression to assign to iterator
            stop - expression to evaluate against to terminate the loop
            step - expression to change the iterator variable each iteration
            *statements - statements to execute in the for loop
        """
        raise NotImplementedError

    @abstractmethod
    def while_loop(self, *statements, condition: Optional[Expression] = None):
        """While loop implementation for a language.
        Arguments:
            condition: condition for when to terminate the loop.
                       If None, an infinte loop is assumed
            *statements - statements to execute in the for loop
        """
        raise NotImplementedError

    def break_loop(self):
        """Language implementation of break"""
        return "break" + self.terminator

    @abstractmethod
    def if_else(
        self,
        condition: Expression,
        true_stmts: List[Expression],
        false_stmts: List[Expression] = None,
    ) -> Expression:
        """If/Else expression in a programming language.
        Provide a condition and execute true (required) or flase statements (optional)
        """
        raise NotImplementedError

    # TODO: add loads of non-abstract common things like
    # equals, less than, array indexing, calling (), addition
    def increment(self, id: str, inc: Expression = None):
        return f"{id} = {id} + {1 if inc is None else inc}"

    def lt(self, lhs: Expression, rhs: Expression):
        return f"{lhs} < {rhs}"

    def leq(self, lhs: Expression, rhs: Expression):
        return f"{lhs} <= {rhs}"

    def gt(self, lhs: Expression, rhs: Expression):
        return f"{lhs} > {rhs}"

    def geq(self, lhs: Expression, rhs: Expression):
        return f"{lhs} >= {rhs}"

    def eq(self, lhs: Expression, rhs: Expression):
        return f"{lhs} == {rhs}"

    def neq(self, lhs: Expression, rhs: Expression):
        return f"{lhs} != {rhs}"

    def negate(self, expr: Expression):
        return f"!({expr})"
