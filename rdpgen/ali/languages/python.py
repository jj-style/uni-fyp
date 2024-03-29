from ..language import Language
from ..types import Type, Composite, Primitive, Expression
from ..utils import imports, expression, convert_case
from ..errors import MissingTypeError
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any
import regex as re


class Python(Language):
    def __init__(
        self,
        expand_tabs: bool = False,
        tab_size: int = 4,
        case: str = "snake",
        declare_vars: bool = True,
        imports: List[str] = [],
        **kwargs,
    ):
        super().__init__(expand_tabs, tab_size, case, imports)
        self.__main_func: bool = False
        self.declare_vars = declare_vars

    @property
    def name(self) -> str:
        return "python"

    @property
    def extension(self) -> str:
        return "py"

    def varn(self, var: str) -> str:
        """don't need to prevent redeclaration for python"""
        return var

    def prelude(self, **kwargs):
        imports = sorted(self.imports)
        includes = ""
        for imp in imports:
            if imp.find(".") < 0:
                # import top-level module
                import_line = f"import {imp}"
            else:
                split = imp.split(".")
                from_ = split[: len(split) - 1]
                import_ = split[-1]
                import_line = f"from {'.'.join(from_)} import {import_}"
            includes += import_line + "\n"

        return includes + "\n\n"

    def postlude(self, **kwargs):
        if self.__main_func:
            return self.if_else(
                self.eq("__name__", self.string("__main__")), [self.call("main")]
            )
        return ""

    def types(self, t: Type) -> str:
        if isinstance(t, Primitive):
            if t is Primitive.Int:
                return "int"
            elif t is Primitive.Float:
                return "float"
            elif t is Primitive.String:
                return "str"
            elif t is Primitive.Bool:
                return "bool"
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                self.import_package("typing.List")
                return f"List[{self.types(t.sub)}]"

    def string(self, s: str, double: bool = True):
        return f'"{s}"' if double else f"'{s}'"

    def string_split(self, s: str, delim: str):
        return f"{s}.{self.call('split', delim)}"

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"[{joined}]"

    def array_length(self, expression):
        return self.call("len", expression)

    @convert_case(0)
    def array_append(self, id: str, item):
        return self.call(f"{id}.append", str(item))

    @convert_case(0)
    def array_remove(self, id: str, idx: int):
        return self.call(f"{id}.pop", idx)

    @convert_case(0, 1)
    @expression
    def array_iterate(
        self,
        id: str,
        it: str,
        *statements,
        declare_it: bool = True,
        iterate_items: bool = False,
        type: Type = None,
    ):
        stmts = []
        if declare_it:
            if iterate_items:
                if type is None:
                    raise MissingTypeError()
                stmts.append(self.declare(it, type))
            else:
                stmts.append(self.declare(it, Primitive.Int))

        if iterate_items:
            stmts.append(f"for {it} in {id}{self.block(*statements)}")
        else:
            stmts.append(
                f"for {it} in {self.call('range', self.array_length(id))}{self.block(*statements)}"  # noqa
            )

        return self.linesep.join([stmts[0]] + [self.indent(s) for s in stmts[1:]])

    @convert_case(0, 1, 2)
    @expression
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
        stmts = []
        if declare_it:
            stmts.append(self.declare(it, Primitive.Int))
        if declare_item:
            if type is None:
                raise MissingTypeError()
            stmts.append(self.declare(item, type))
        stmts.append(
            f"for {it}, {item} in {self.call('enumerate', id)}{self.block(*statements)}"
        )
        return self.linesep.join([self.indent(s) for s in stmts])

    @convert_case(0)
    @imports("typing.get_type_hints")
    def declare(self, id: str, type: Type):
        if self.declare_vars:
            return f"{id}: {self.types(type)}"
        else:
            self.imports.discard("typing.get_type_hints")
            return ""

    @convert_case(0)
    def assign(self, id: str, expr):
        return f"{id} = {expr}"

    @convert_case(0)
    @expression
    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type], None],
        *statements,
    ):
        if id == "main":
            self.__main_func = True

        args = format_function_arguments(arguments)
        arg_list = ", ".join([f"{name}: {self.types(t)}" for name, t in args.items()])
        ret_part = "" if return_type is None else " -> " + self.types(return_type)

        stmts = self.block(*statements)
        func = f"def {id}({arg_list}){ret_part}{stmts}"
        return func

    def block(self, *statements):
        block = f":{self.linesep}"
        self.indent_lvl += 1
        for stmt in statements:
            if stmt == "":
                continue
            block += self.indent(str(stmt)) + self.linesep
        self.indent_lvl -= 1
        return block.rstrip(self.linesep)

    def do_nothing(self):
        return "pass"

    def comment(self, comment: str):
        lines = comment.split(self.linesep)
        if len(lines) == 1:
            return f"# {lines[0]}"
        multiline = '"""\n'
        for line in lines:
            multiline += line + "\n"
        multiline += '"""\n'
        return multiline

    def do_return(self, expression=None):
        if expression is None:
            return "return"
        else:
            return f"return {expression}"

    def println(self, *args) -> str:
        return f"""print({", ".join([str(a) for a in args])})"""

    def print(self, *args) -> str:
        print(f"""print({", ".join([str(a) for a in args])}, end="")""")
        return f"""print({", ".join([str(a) for a in args])}, end="")"""

    @convert_case(0)
    @expression
    def for_loop(
        self,
        it: str,
        start,
        stop,
        step,
        *statements,
    ):
        # to keep for loops generic and not restricted we will implement a for loop
        # with a while loop so the step function can be generic and not restricted
        # to an integer step size

        # match stopping condition and stepping condition on regexes
        # if match a simple "iterator [<>] <something>" and
        # "iterator" = "iterator" [+-] <step_size>
        # then convert it to a pythonic range for loop
        m1 = re.match(rf"{it}\s*(?P<condition>(<|>))\s*(?P<end>.*$)", stop)
        m2 = re.match(
            rf"{it}\s*(=\s*{it}\s*(?P<op>[+-])\s*(?P<size>\d+)|(?P<op>[+-])\s*=\s*(?P<size>\d+))$",  # noqa
            step,
        )

        if m1 and m2:
            range_groups = m1.groupdict()
            range_steps = m2.groupdict()
            decreasing = range_steps["op"] == "-"
            return f"for {it} in range({start}, {range_groups['end']}, {'-' if decreasing else ''}{range_steps['size']}){self.block(*statements)}"  # noqa

        statements = [
            *statements,
            step,
        ]
        return (
            str(self.assign(it, start))
            + self.linesep
            + self.indent(str(self.while_loop(*statements, condition=stop)))
        )

    @expression
    def while_loop(self, *statements, condition=None):
        stmts = list(statements)
        if condition is not None:
            stmts.insert(0, self.if_else(self.negate(condition), [self.break_loop()]))
        loop = f"while True{self.block(*stmts)}"
        return loop

    @expression
    def if_else(
        self,
        condition,
        true_stmts,
        false_stmts=None,
    ):
        else_if = (
            false_stmts
            and len(false_stmts) == 1
            and re.match(r"if\s.*", str(false_stmts[0]))
        )
        if else_if:
            return f"if {condition}{self.block(*true_stmts)}{self.linesep}{self.indent('el'+str(false_stmts[0]))}"  # noqa

        expr = f"if {condition}{self.block(*true_stmts)}"
        if false_stmts:
            expr += self.linesep + self.indent(f"{('else' + self.block(*false_stmts))}")
        return expr

    def negate(self, expr: Expression):
        return f"not ({expr})"

    def bool_and(self, expr1, expr2):
        return f"{expr1} and {expr2}"

    def bool_or(self, expr1, expr2):
        return f"{expr1} or {expr2}"

    def true(self):
        return "True"

    def false(self):
        return "False"

    @imports("subprocess")
    @expression
    def command(
        self, command: str, suppress_output: bool = True, exit_on_failure: bool = True
    ):
        cmd = command.replace('"', '"')
        subprocess_opts = [
            "shell=True",
            "stdout=subprocess.DEVNULL",
            "stderr=subprocess.DEVNULL",
        ]
        if not suppress_output:
            subprocess_opts = subprocess_opts[:1]

        stmts = []
        if exit_on_failure:
            stmts.append(
                self.assign(
                    "response",
                    self.call("subprocess.run", cmd, *subprocess_opts),
                )
            )
            stmts.append(
                self.if_else(self.neq("response.returncode", 0), [self.exit(code=1)])
            )
        else:
            stmts.append(self.call("subprocess.run", cmd, *subprocess_opts))
        return self.linesep.join([stmts[0]] + [self.indent(s) for s in stmts[1:]])

    def exit(self, code: int = 0):
        return self.call("exit", code)

    def read_lines(self, file: str):
        func_name = "read_lines"

        def lib():
            s1 = self.assign("f", self.call("open", "file", self.string("r")))
            s2 = self.assign("text", self.call("f.read"))
            s3 = self.call("f.close")
            s4 = self.do_return(expression=self.call("text.splitlines"))
            stmts = [s1, s2, s3, s4]
            return self.function(
                func_name,
                Composite.array(Primitive.String),
                {"file": Primitive.String},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)

    def read_file(self, file: str):
        func_name = "read_file"

        def lib():
            s1 = self.assign("f", self.call("open", "file", self.string("r")))
            s2 = self.assign("content", self.call("f.read"))
            s3 = self.call("f.close")
            s4 = self.do_return(expression="content")
            stmts = [s1, s2, s3, s4]
            return self.function(
                func_name, Primitive.String, {"file": Primitive.String}, *stmts
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)

    @expression
    @imports("sys")
    def read_file_stdin(self):
        func_name = "read_file_stdin"

        def lib():
            s1 = self.assign("content", self.string(""))
            s2 = self.array_iterate(
                "sys.stdin",
                "line",
                self.increment("content", "line"),
                declare_it=False,
                iterate_items=True,
            )
            s3 = self.do_return(expression="content")
            stmts = [s1, s2, s3]
            return self.function(func_name, Primitive.String, None, *stmts)

        self.register_helper(func_name, lib())
        return self.call(func_name)

    @imports("sys")
    def argc(self):
        return self.array_length("sys.argv")

    @imports("sys")
    def argv(self):
        return "sys.argv"
