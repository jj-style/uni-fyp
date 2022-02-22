from abc import ABC, abstractmethod
from typing import Union, Dict, List, Optional, Any, Callable
import os

from .types import Type, Expression


class Context:
    """Context for language"""

    def __init__(
        self,
        expand_tabs: bool = False,
        tab_size: int = 2,
        case_converter: Callable[[str], str] = None,
    ):
        self.indent_lvl: int = 0
        self.expand_tabs: bool = expand_tabs
        self.tab_size: int = tab_size
        self.case_convert = lambda s: s if case_converter is None else case_converter


class Language(ABC):
    def __init__(self, ctx: Context = None):
        self.__var_dec_count = {}
        self.imports = set()
        self.helper_funcs = {}
        self.ctx = Context() if not ctx else ctx

    def register_helper(self, name, func):
        self.helper_funcs[name] = func

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the language"""
        raise NotImplementedError

    @property
    @abstractmethod
    def extension(self) -> str:
        """Extension of files for this language without the dot"""
        raise NotImplementedError

    def varn(self, var: str) -> str:
        """Obtain a numbered variable to prevent redeclaration"""
        if var not in self.__var_dec_count:
            self.__var_dec_count[var] = 0
            return var

        self.__var_dec_count[var] += 1
        return f"{var}{self.__var_dec_count[var]}"

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

    def postlude(self, **kwargs):
        """Program can generate postlude after the code"""
        return ""

    @abstractmethod
    def types(self, t: Type) -> str:
        """How a language represents a type"""
        raise NotImplementedError

    @abstractmethod
    def string(self, s: str, double: bool = True):
        """Construct a string in a language

        Args:
            s (str): the string to construct
            double (bool): whether to surround in double quotes or single
        """
        raise NotImplementedError

    @abstractmethod
    def string_split(self, s: str, delim: str):
        """Split a string into a list of strings based on a delimiter"""
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
    def array_length(self, expression):
        """Get the lenght of an array"""
        raise NotImplementedError

    @abstractmethod
    def array_append(self, id: str, item):
        """Append an item to the end of an array"""
        raise NotImplementedError

    @abstractmethod
    def array_remove(self, id: str, idx: int):
        """Delete the item at index idx from the array called id"""
        raise NotImplementedError

    @abstractmethod
    def array_iterate(
        self,
        id: str,
        it: str,
        *statements,
        declare_it: bool = True,
        iterate_items: bool = False,
        type: Type = None,
    ):
        """Iterate over an array with a named iterator variable
        Arguments:
            id: str - name of the array to iterate over
            it: str - name of the iterator variable
            *statements - statements to execute in loop
            declare_it: bool - if True, will declare the variable first (default = True)
            iterate_items: bool - if True, will iterate over the items in the array not the indices (False)
            type: Type - type of items in the array, required if iterate_items is True
        """  # noqa
        raise NotImplementedError

    @abstractmethod
    def array_enumerate(
        self,
        id: str,
        it: str,
        item: str,
        *statements,
        declare_it: bool = True,
        declare_item: bool = False,
        type: Type = None,
    ):
        """Enumerate over an array with a named iterator variable and item variable
        Arguments:
            id: str - name of the array to iterate over
            it: str - name of the iterator variable
            item: str - name of variable of each item
            *statements - statements to execute in loop
            declare_it: bool - if True, will declare the variable first (default = True)
            declare_item: bool - if True, will declare the variable first (default = False)
            type: Type - type of elements in the array. Required if declare_item is True (default = None)
        """  # noqa
        raise NotImplementedError

    def index(self, expression, offset):
        """Index an array"""
        return f"{expression}[{offset}]"

    def call(self, expression, *args):
        """Call a function/method"""
        return f"{expression}({', '.join(str(a) for a in list(args))})"

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
        """A function in a language
        Arguments:
            id: str - name of the function
            return_type: Optional[Type] - return type of the function
            arguments: Union[Dict[str, Type], List[Type], None] - arguments to the function
            *statements - all statements that should be in the body of the function
        """  # noqa
        raise NotImplementedError

    @abstractmethod
    def block(self, *statements):
        """Block concept in a language,
        defining a scope and indentation for statements
        """
        raise NotImplementedError

    def do_nothing(self):
        """Do nothing"""
        return ""

    def comment(self, comment: str):
        """Insert a comment in the language.
        If not overidden, defaults to C-like comments"""
        lines = comment.split(self.linesep)
        if len(lines) == 1:
            return f"// {lines[0]}"
        multiline = "/*\n"
        for line in lines:
            multiline += line + "\n"
        multiline += "*/\n"
        return multiline

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
        """Increment a variable identified with `id`, with an optional increment value.
        If not specified, defaults to 1.
        """
        return f"{id} = {id} + {1 if inc is None else inc}{self.terminator}"

    def decrement(self, id: str, dec: Expression = None):
        """Decrement a variable identified with `id`, with an optional decrement value.
        If not specified, defaults to 1.
        """
        return f"{id} = {id} - {1 if dec is None else dec}{self.terminator}"

    def add(self, lhs, rhs):
        """Add 2 expressions"""
        return f"{lhs} + {rhs}"

    def sub(self, lhs, rhs):
        """Subtract 2 expressions"""
        return f"{lhs} - {rhs}"

    def lt(self, lhs: Expression, rhs: Expression):
        """Less than between 2 expressions"""
        return f"{lhs} < {rhs}"

    def leq(self, lhs: Expression, rhs: Expression):
        """Less than or equal between 2 expressions"""
        return f"{lhs} <= {rhs}"

    def gt(self, lhs: Expression, rhs: Expression):
        """Greater than between 2 expressions"""
        return f"{lhs} > {rhs}"

    def geq(self, lhs: Expression, rhs: Expression):
        """Greater than or equal between 2 expressions"""
        return f"{lhs} >= {rhs}"

    def eq(self, lhs: Expression, rhs: Expression):
        """Equate 2 expressions"""
        return f"{lhs} == {rhs}"

    def neq(self, lhs: Expression, rhs: Expression):
        """Not equal for 2 expressions"""
        return f"{lhs} != {rhs}"

    def negate(self, expr: Expression):
        """Negate an expressions"""
        return f"!({expr})"

    def bool_and(self, expr1, expr2):
        """Boolean AND operation between 2 expressions"""
        return f"{expr1} && {expr2}"

    def bool_or(self, expr1, expr2):
        """Boolean AND operation between 2 expressions"""
        return f"{expr1} || {expr2}"

    def true(self):
        """True boolean. Defaults to lowercase C-like booleans"""
        return "true"

    def false(self):
        """False boolean. Defaults to lowercase C-like booleans"""
        return "false"

    # TODO: stdlib like fileio, readlines, read/write etc.

    @abstractmethod
    def command(
        self, command: str, suppress_output: bool = True, exit_on_failure: bool = True
    ):
        """Invoke an operating system command
        Arguments:
            command: str - command to execute on the command line

        Optional Arguments:
            suppress_output: bool - show/supress the output of the command on stdout [default True]
            exit_on_failure: bool - whether the code should exit on failure [default True]
        """  # noqa: E501
        raise NotImplementedError

    @abstractmethod
    def exit(self, code: int = 0):
        """Exit the program with an optional status code, defaulting to 0"""
        raise NotImplementedError

    @abstractmethod
    def read_lines(self, file: str):
        """Open a file and read the lines into a list of strings"""
        raise NotImplementedError

    @abstractmethod
    def read_file(self, file: str):
        """Open a file and read the contents into a string"""
        raise NotImplementedError

    @abstractmethod
    def read_file_stdin(self):
        """Read until EOF from standard input"""
        raise NotImplementedError

    @abstractmethod
    def argc(self):
        """Access to command line argument count."""
        raise NotImplementedError

    @abstractmethod
    def argv(self):
        """Access to command line argument as a list of strings."""
        raise NotImplementedError
