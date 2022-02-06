from ..language import (
    Language,
    Type,
    imports,
    Primitive,
    Composite,
    expression,
    MissingTypeError,
)
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
        else:
            return str(t)

    def string(self, s: str):
        return f'"{s}"'

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"{{{joined}}}"

    def array_length(self, expression):
        return f"{expression}.size()"

    def array_append(self, id: str, item):
        return self.call(f"{id}.push_back", str(item)) + self.terminator

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
            else:
                stmts.append(self.declare(it, Primitive.Int))

        if iterate_items:
            stmts.append(
                f"for ({self.types(type)} {it} : {id}) {self.block(*statements)}"
            )
        else:
            stmts.append(
                self.for_loop(
                    it,
                    0,
                    self.lt(it, self.array_length(id)),
                    self.increment(it),
                    *statements,
                )
            )

        return self.linesep.join([self.indent(s) for s in stmts])

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
        if declare_item:
            if type is None:
                raise MissingTypeError()
            stmts.append(self.declare(item, type))
        loop_stmts = [self.assign(item, self.index(id, it)), *statements]
        stmts.append(self.array_iterate(id, it, *loop_stmts, declare_it=declare_it))
        return self.linesep.join([self.indent(s) for s in stmts])

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

    @imports("stdlib.h")
    def command(
        self, command: str, suppress_output: bool = True, exit_on_failure: bool = True
    ):
        cmd = command.replace('"', '\\"')
        if suppress_output:
            cmd += " > /dev/null 2>&1"
        stmts = []
        if exit_on_failure:
            stmts.append(self.declare("rc", Primitive.Int))
            stmts.append(self.assign("rc", self.call("system", self.string(cmd))))
        else:
            stmts.append(self.call("system", self.string(cmd)) + self.terminator)
        if exit_on_failure:
            stmts.append(self.if_else(self.neq("rc", 0), [self.exit(1)]))

        return self.linesep.join([self.indent(s) for s in stmts])

    @imports("stdlib.h")
    def exit(self, code: int = 0):
        return self.call("exit", code) + self.terminator

    @imports("iostream", "fstream")
    def read_lines(self, file: str):
        func_name = "read_lines"

        def lib():
            s1 = self.declare("f", "std::fstream")
            s2 = self.declare("lines", Composite.array(Primitive.String))
            s3 = self.call("f.open", "file", "std::ios::in") + self.terminator
            s4 = self.if_else(
                self.call("f.is_open"),
                [
                    self.declare("line", Primitive.String),
                    self.while_loop(
                        self.array_append("lines", "line"),
                        condition=self.call("getline", "f", "line"),
                    ),
                    self.call("f.close") + self.terminator,
                ],
                false_stmts=[self.exit(1)],
            )
            s5 = self.do_return(expression="lines")
            stmts = [s1, s2, s3, s4, s5]
            return self.function(
                func_name,
                Composite.array(Primitive.String),
                {"file": Primitive.String},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)
