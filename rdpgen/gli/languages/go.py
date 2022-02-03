from ..language import Language, Type, imports, expression, Primitive, Composite
from .utils import format_function_arguments
from typing import Dict, Union, Optional, List, Any
import shlex


class Go(Language):
    @property
    def name(self) -> str:
        return "golang"

    def prelude(self, **kwargs):
        package = kwargs.get("package", "main")
        imports = ""
        if len(self.imports) > 0:
            pkgs = "\n".join(
                self.whitespace_char + self.string(pkg) for pkg in self.imports
            )
            imports = f"import (\n{pkgs}\n)\n\n"
        return f"package {package}\n\n{imports}"

    def types(self, t: Type) -> str:
        if isinstance(t, Primitive):
            if t is Primitive.Int:
                return "int"
            elif t is Primitive.Float:
                return "float64"
            elif t is Primitive.String:
                return "string"
        elif isinstance(t, Composite):
            if t.base is Composite.CType.Array:
                return f"[]{self.types(t.sub)}"
        else:
            # allow special types in certain functions
            # e.g. command() needs type Cmd
            return str(t)

    def string(self, s: str):
        return f'"{s}"'

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"[]{self.types(t)}{{{joined}}}"

    def array_length(self, expression):
        return f"len({expression})"

    def declare(self, id: str, type: Type):
        return f"var {id} {self.types(type)}"

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
        args = format_function_arguments(arguments)
        arg_list = ", ".join([f"{name} {self.types(t)}" for name, t in args.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)

        stmts = self.block(*statements)
        func = f"func {id}({arg_list}){ret_part} {stmts}"
        return func

    def block(self, *statements):
        block = f"{{{self.linesep}"
        self.ctx.indent_lvl += 1
        for stmt in statements:
            block += self.indent(str(stmt)) + self.linesep
        self.ctx.indent_lvl -= 1
        block += "}"
        return block

    def do_return(self, expression=None):
        if expression is None:
            return "return"
        else:
            return f"return {expression}"

    @imports("fmt")
    def println(self, *args) -> str:
        return f"""fmt.Println({", ".join([str(a) for a in args])})"""

    @imports("fmt")
    def print(self, *args) -> str:
        return f"""fmt.Print({", ".join([str(a) for a in args])})"""

    @expression
    def for_loop(
        self,
        it: str,
        start,
        stop,
        step,
        *statements,
    ):
        return f"for {self.assign(it, start)}; {stop}; {step} {self.block(*statements)}"

    @expression
    def while_loop(self, *statements, condition=None):
        stmts = list(statements)
        if condition is not None:
            stmts.insert(0, self.if_else(self.negate(condition), [self.break_loop()]))
        loop = f"for {self.block(*stmts)}"
        return loop

    @expression
    def if_else(
        self,
        condition,
        true_stmts,
        false_stmts=None,
    ):
        return f"if {condition} {self.block(*true_stmts)}{(' else ' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa

    @imports("os/exec")
    def command(self, command: str, suppress_output: bool = True):
        stmts = []
        args = [f'"{a}"' for a in shlex.split(command)]
        if suppress_output:
            stmts.append(self.declare("cmd", "*exec.Cmd"))
            stmts.append(
                self.assign(
                    "cmd",
                    self.call("exec.Command", *args),
                )
            )
            stmts.append(self.assign("_", self.call("cmd.Run")))

        else:
            stmts.append(self.declare("out", Composite.array("byte")))
            stmts.append(
                self.assign(
                    "out, _",
                    self.call("exec.Command", *args) + f".{self.call('Output')}",
                )
            )
            stmts.append(self.println("string(out)"))

        stmts = [self.indent(s) for s in stmts]
        return self.linesep.join(stmts)
