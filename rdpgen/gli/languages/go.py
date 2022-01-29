from ..language import Language, Type, imports, expression, Primitive, Composite
from typing import Dict, Union, Optional, List, Any


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

    def string(self, s: str):
        return f'"{s}"'

    def array(self, t: Type, elements: List[Any]):
        joined = ", ".join(str(e) for e in elements)
        return f"{self.types(t)}{{{joined}}}"

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
        args = {} if not arguments else arguments
        if isinstance(arguments, list):
            # not got named arguments to use so use arg1,..,argn
            args = {f"arg{idx+1}": self.types(t) for idx, t in enumerate(arguments)}

        arg_list = ", ".join([f"{name} {t}" for name, t in args.items()])
        ret_part = "" if return_type is None else " " + self.types(return_type)

        stmts = self.block(*statements)
        return f"func {id}({arg_list}){ret_part} {stmts}"

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

    def for_loop(
        self,
        it: str,
        start,
        stop,
        step,
        *statements,
    ):
        return f"for {self.assign(it, start)}; {stop}; {step} {self.block(*statements)}"

    def if_else(
        self,
        condition,
        true_stmts,
        false_stmts=None,
    ):
        return f"if {condition} {self.block(*true_stmts)}{(' else ' + self.block(*false_stmts)) if false_stmts else ''}"  # noqa
