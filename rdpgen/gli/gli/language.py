from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Union, Dict, List, Optional
import os


class Type(Enum):
    Int = auto()
    Float = auto()
    String = auto()


def imports(*packages):
    def import_wrapper(func):
        def wrap(self, *args, **kwargs):
            for pkg in packages:
                self.import_package(pkg)
            return func(self, *args, **kwargs)

        return wrap

    return import_wrapper


class Expression:
    def __init__(self, body):
        self.body = body

    def __str__(self):
        return str(self.body)


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

    @abstractmethod
    def types(self, t: Type) -> str:
        """How a language represents a type"""
        raise NotImplementedError

    @abstractmethod
    def string(self, s: str) -> Expression:
        """Construct a string in a language

        Args:
            s (str): the string to construct
        """
        raise NotImplementedError

    @abstractmethod
    def declare(self, id: str, type: Type) -> Expression:
        """Declare a variable

        Args:
            id (str): identifier of the variable to declare
            type (Type): the type of the variable
        """
        raise NotImplementedError

    @abstractmethod
    def assign(self, id: str, expr: Expression) -> Expression:
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
        arguments: Union[Dict[str, Type], List[Type]],
        *statements
    ) -> Expression:
        # TODO - add documentation
        raise NotImplementedError

    @abstractmethod
    def block(self, *statements) -> Expression:
        """Block concept in a language,
        defining a scope and indentation for statements
        """
        raise NotImplementedError

    @abstractmethod
    def do_return(self, expression: Optional[Expression]) -> Expression:
        # TODO - add documentation
        raise NotImplementedError

    @abstractmethod
    def println(self, *args) -> str:
        """Prints values to stdout with a newline at the end"""
        raise NotImplementedError

    @abstractmethod
    def print(self, *args) -> str:
        """Prints values to stdout"""
        raise NotImplementedError
