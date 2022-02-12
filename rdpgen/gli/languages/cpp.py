from ..language import Language
from ..types import Type, Primitive, Composite
from ..utils import imports, expression
from ..errors import MissingTypeError
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any
import regex


class Cpp(Language):
    @property
    def name(self) -> str:
        return "c++"

    @property
    def extension(self) -> str:
        return "cpp"

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
            elif t is Primitive.Bool:
                return "bool"
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                self.import_package("vector")
                return f"std::vector<{self.types(t.sub)}>"
        else:
            return str(t)

    def string(self, s: str, double: bool = True):
        return f'"{s}"' if double else f"'{s}'"

    @imports("sstream")
    def string_split(self, s: str, delim: str):
        func_name = "split_string"

        def lib():
            s1 = self.declare("tmp", Primitive.String)
            s2 = self.call("std::stringstream ss", "s") + self.terminator
            s3 = self.declare("words", Composite.array(Primitive.String))
            s4 = self.while_loop(
                self.array_append("words", "tmp"),
                condition=self.call("std::getline", "ss", "tmp", "delim"),
            )
            s5 = self.do_return(expression="words")
            stmts = [s1, s2, s3, s4, s5]
            return self.function(
                func_name,
                Composite.array(Primitive.String),
                {"s": Primitive.String, "delim": "char"},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, s, delim.replace('"', "'"))

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"{{{joined}}}"

    def array_length(self, expression):
        return f"{expression}.size()"

    def array_append(self, id: str, item):
        return self.call(f"{id}.push_back", str(item)) + self.terminator

    def array_remove(self, id: str, idx: int):
        return (
            self.call(f"{id}.erase", self.add(self.call(f"{id}.begin"), idx))
            + self.terminator
        )

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
                self.indent(
                    self.for_loop(
                        it,
                        0,
                        self.lt(it, self.array_length(id)),
                        self.increment(it),
                        *statements,
                    )
                )
            )

        return self.linesep.join(stmts)

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
        stmts.append(
            self.indent(self.array_iterate(id, it, *loop_stmts, declare_it=declare_it))
        )
        return self.linesep.join(stmts)

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
                arg_list = "int argc, char* argv[]"
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
        block += self.indent("}") if self.ctx.indent_lvl > 0 else "}"
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
        else_if = (
            false_stmts
            and len(false_stmts) == 1
            and regex.match(r"if\s.*", str(false_stmts[0]))
        )
        if else_if:
            return f"if ({condition}) {self.block(*true_stmts)} else {false_stmts[0]}"

        return f"if ({condition}) {self.block(*true_stmts)}{(' else ' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa

    @imports("stdlib.h")
    @expression
    def command(
        self, command: str, suppress_output: bool = True, exit_on_failure: bool = True
    ):
        stmts = []
        stmts.append(self.declare("cmd", Primitive.String))
        stmts.append(self.assign("cmd", command))
        if suppress_output:
            stmts.append(
                self.assign("cmd", self.add("cmd", self.string(" > /dev/null 2>&1")))
            )
        if exit_on_failure:
            stmts.append(self.declare("rc", Primitive.Int))
            stmts.append(self.assign("rc", self.call("system", self.call("cmd.c_str"))))
        else:
            stmts.append(
                self.call("system", self.call("cmd.c_str()")) + self.terminator
            )
        if exit_on_failure:
            stmts.append(self.if_else(self.neq("rc", 0), [self.exit(1)]))

        return self.linesep.join([stmts[0]] + [self.indent(s) for s in stmts[1:]])

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

    @imports("iostream", "fstream")
    def read_file(self, file: str):
        func_name = "read_file"

        def lib():
            s1 = self.declare("f", "std::fstream")
            s2 = self.declare("content", Primitive.String)
            s3 = self.call("f.open", "file", "std::ios::in") + self.terminator
            s4 = self.if_else(
                self.call("f.is_open"),
                [
                    self.declare("line", Primitive.String),
                    self.while_loop(
                        self.increment(
                            "content",
                            inc=self.add("line", self.string(r"\n")),
                        ),
                        condition=self.call("getline", "f", "line"),
                    ),
                    self.call("f.close") + self.terminator,
                ],
                false_stmts=[self.exit(1)],
            )
            s5 = self.do_return(expression="content")
            stmts = [s1, s2, s3, s4, s5]
            return self.function(
                func_name,
                Primitive.String,
                {"file": Primitive.String},
                *stmts,
            )

        self.register_helper(func_name, lib())
        return self.call(func_name, file)

    def argc(self):
        return "argc"

    def argv(self):
        return "argv"
