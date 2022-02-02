from ..language import Language, Type, imports, Primitive, Composite, expression
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any


class Cpp(Language):
    @property
    def name(self) -> str:
        return "c++"

    @property
    def terminator(self) -> str:
        return ";"

    def prelude(self, **kwargs):
        includes = "\n".join(f"#include <{pkg}>" for pkg in sorted(self.imports))
        return includes + "\n\n"

    def types(self, t: Type) -> str:
        if isinstance(t, Primitive):
            if t is Primitive.Int:
                return "int"
            elif t is Primitive.Float:
                return "double"
            elif t is Primitive.String:
                self.import_package("string")
                return "std::string"
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                self.import_package("vector")
                return f"std::vector<{self.types(t.sub)}>"

    def string(self, s: str):
        return f'"{s}"'

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"{{{joined}}}"

    def array_length(self, expression):
        return f"{expression}.size()"

    def declare(self, id: str, type: Type):
        return f"{self.types(type)} {id}{self.terminator}"

    def assign(self, id: str, expr):
        return f"{id} = {expr}{self.terminator}"

    @expression
    def function(
        self,
        id: str,
        return_type: Optional[Type],
        arguments: Union[Dict[str, Type], List[Type]],
        *statements,
    ):
        args = format_function_arguments(arguments)
        arg_list = ", ".join([f"{self.types(t)} {name}" for name, t in args.items()])

        # special logic for main function as has to be int not void
        if return_type is None:
            if id == "main":
                ret_part = self.types(Primitive.Int)
                statements = [*statements, self.do_return("0")]
            else:
                ret_part = "void"
        else:
            ret_part = self.types(return_type)
        stmts = self.block(*statements)
        func = f"{ret_part} {id}({arg_list}) {stmts}"
        return func

    def do_return(self, expression=None):
        if expression is None:
            return f"return{self.terminator}"
        else:
            return f"return {expression}{self.terminator}"

    def block(self, *statements):
        block = f"{{{self.linesep}"
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(str(stmt)) + self.linesep
        self.ctx.indent_lvl -= 1
        block += "}"
        return block

    @imports("iostream")
    def println(self, *args):
        new_args = [*args, "std::endl"]
        return self.print(*new_args)

    @imports("iostream")
    def print(self, *args) -> str:
        a = " << ".join(list(args))
        if len(a) > 0:
            return_s = f"std::cout << {a}{self.terminator}"
        else:
            return_s = f'std::cout << ""{self.terminator}'
        return return_s

    @expression
    def for_loop(
        self,
        it: str,
        start,
        stop,
        step,
        *statements,
    ):
        step_expr = str(step).rstrip(";")
        return f"for ({it} = {start}; {stop}; {step_expr}) {self.block(*statements)}"

    @expression
    def while_loop(self, *statements, condition=None):
        if condition is None:
            condition = 1
        loop = f"while ({condition}) {self.block(*statements)}"
        return loop

    @expression
    def if_else(
        self,
        condition,
        true_stmts,
        false_stmts=None,
    ):
        return f"if ({condition}) {self.block(*true_stmts)}{(' else ' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa
