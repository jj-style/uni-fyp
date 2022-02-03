from ..language import (
    Language,
    Type,
    imports,
    expression,
    Primitive,
    Composite,
    Context,
    Expression,
)
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any


class Python(Language):
    def __init__(self, ctx: Context = None):
        super().__init__(ctx)
        self.__main_func: bool = False

    @property
    def name(self) -> str:
        return "python"

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
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                self.import_package("typing.List")
                return f"List[{self.types(t.sub)}]"

    def string(self, s: str):
        return f'"{s}"'

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"[{joined}]"

    def array_length(self, expression):
        return f"len({expression})"

    @imports("typing.get_type_hints")
    def declare(self, id: str, type: Type):
        return f"{id}: {self.types(type)}"

    def assign(self, id: str, expr):
        return f"{id} = {expr}"

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
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(str(stmt)) + self.linesep
        self.ctx.indent_lvl -= 1
        return block

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

        # TODO: could add case for python: if step ~= /<it> = <it> + <step>/ -> step -> for i in range :) # noqa

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
        return f"if {condition}{self.block(*true_stmts)}{('else' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa

    def negate(self, expr: Expression):
        return f"not ({expr})"

    @imports("subprocess")
    def command(self, command: str, suppress_output: bool = True):
        cmd = command.replace('"', '\\"')
        subprocess_opts = [
            "shell=True",
            "stdout=subprocess.DEVNULL",
            "stderr=subprocess.DEVNULL",
        ]
        if not suppress_output:
            subprocess_opts = subprocess_opts[:1]
        return self.call("subprocess.run", f'"{cmd}"', *subprocess_opts)